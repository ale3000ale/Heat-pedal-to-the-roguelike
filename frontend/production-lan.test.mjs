import assert from 'node:assert/strict';
import http from 'node:http';
import { once } from 'node:events';
import test from 'node:test';
import { createHeatServer, validateOrigin, gatewayHost } from './production-server.mjs';

async function listen(server) {
	server.listen(0, '127.0.0.1');
	await once(server, 'listening');
	return server.address().port;
}

function request(port, path, headers = {}, method = 'GET') {
	return new Promise((resolve, reject) => {
		const req = http.request({ hostname: '127.0.0.1', port, path, method, headers }, (res) => {
			let body = '';
			res.setEncoding('utf8');
			res.on('data', (chunk) => (body += chunk));
			res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body }));
		});
		req.on('error', reject);
		req.end();
	});
}

function close(server) {
	server.closeAllConnections();
	return new Promise((resolve) => server.close(resolve));
}

test('LAN validation and bind selection reject public HTTP and noncanonical IPv4', () => {
	for (const ip of ['10.0.0.2', '172.16.1.2', '172.31.1.2', '192.168.1.50']) {
		assert.equal(gatewayHost(`http://${ip}:5173`), ip);
	}
	assert.equal(gatewayHost('https://heat.loca.lt'), '127.0.0.1');
	assert.equal(gatewayHost('http://127.0.0.1:5173'), '127.0.0.1');
	for (const value of [
		'http://8.8.8.8:5173',
		'http://169.254.1.2:5173',
		'http://172.32.0.1:5173',
		'http://192.168.1.2',
		'http://0.0.0.0:5173',
		'http://192.168.01.2:5173',
		'http://0xc0a80102:5173',
		'https://x/a',
		'https://u:p@x',
		'https://x#'
	]) {
		assert.throws(() => validateOrigin(value), value);
	}
});

for (const origin of ['https://heat.loca.lt', 'http://192.168.1.50:5173']) {
	test(`Host, Origin, cookies, media, SSE and forwarding: ${origin}`, async () => {
		const url = new URL(origin);
		const backend = http.createServer((req, res) => {
			if (req.url === '/api/events/stream') {
				res.setHeader('Content-Type', 'text/event-stream');
				res.write('data: first\n\n');
				setTimeout(() => res.end('data: last\n\n'), 10);
			} else {
				res.setHeader('Set-Cookie', ['a=1; HttpOnly', 'b=2; SameSite=Lax']);
				res.end(
					JSON.stringify({
						url: req.url,
						proto: req.headers['x-forwarded-proto'],
						host: req.headers['x-forwarded-host'],
						cookie: req.headers.cookie
					})
				);
			}
		});
		const backendPort = await listen(backend);
		const gateway = createHeatServer({
			origin,
			backendPort,
			readyToken: 'test-token',
			handler: (req, res) => res.end('frontend')
		});
		const port = await listen(gateway);
		const host = { host: url.host };
		try {
			assert.equal((await request(port, '/', { host: 'evil.test' })).status, 421);
			assert.equal((await request(port, '/api/login', host, 'POST')).status, 403);
			assert.equal(
				(await request(port, '/api/login', { ...host, origin: 'http://evil.test' }, 'POST')).status,
				403
			);
			assert.equal((await request(port, '//evil.test', host)).status, 400);
			assert.equal((await request(port, '/', host)).body, 'frontend');
			const login = await request(
				port,
				'/api/login',
				{
					...host,
					origin,
					cookie: 'heat_session=example',
					'x-forwarded-proto': 'evil',
					'x-forwarded-host': 'evil.test'
				},
				'POST'
			);
			assert.equal(login.status, 200);
			assert.equal(JSON.parse(login.body).proto, url.protocol.slice(0, -1));
			assert.equal(JSON.parse(login.body).host, url.host);
			assert.equal(JSON.parse(login.body).cookie, 'heat_session=example');
			assert.equal(login.headers['set-cookie'].length, 2);
			assert.equal(
				JSON.parse((await request(port, '/media/cards/a.webp', host)).body).url,
				'/media/cards/a.webp'
			);
			const stream = await request(port, '/api/events/stream', host);
			assert.equal(stream.headers['content-type'], 'text/event-stream');
			assert.equal(stream.body, 'data: first\n\ndata: last\n\n');
			assert.deepEqual(JSON.parse((await request(port, '/__heat_ready', host)).body), {
				token: 'test-token'
			});
		} finally {
			await close(gateway);
			await close(backend);
		}
	});
}
