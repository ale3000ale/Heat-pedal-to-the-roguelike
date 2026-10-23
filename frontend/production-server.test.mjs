import assert from 'node:assert/strict';
import http from 'node:http';
import { once } from 'node:events';
import test from 'node:test';
import { createHeatServer, validateOrigin } from './production-server.mjs';

async function listen(server) {
	server.listen(0, '127.0.0.1');
	await once(server, 'listening');
	return server.address().port;
}

function request(port, path, headers = {}, method = 'GET') {
	return new Promise((resolve, reject) => {
		const req = http.request(
			{ hostname: '127.0.0.1', port, path, method, headers },
			(res) => {
				let body = '';
				res.setEncoding('utf8');
				res.on('data', (chunk) => (body += chunk));
				res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body }));
			}
		);
		req.on('error', reject);
		req.end();
	});
}

function close(server) {
	server.closeAllConnections();
	return new Promise((resolve) => server.close(resolve));
}

test('explicit origin validation', () => {
	assert.equal(validateOrigin('https://heat.loca.lt').origin, 'https://heat.loca.lt');
	for (const value of ['http://evil.test', 'https://x/a', 'https://u:p@x', 'https://x#']) {
		assert.throws(() => validateOrigin(value));
	}
});

test('gateway restricts hosts and origins, preserves cookies, media and SSE', async () => {
	const backend = http.createServer((req, res) => {
		if (req.url === '/api/events/stream') {
			res.setHeader('Content-Type', 'text/event-stream');
			res.write('data: first\n\n');
			setTimeout(() => res.end('data: last\n\n'), 10);
		} else {
			res.setHeader('Set-Cookie', ['a=1; HttpOnly', 'b=2; Secure']);
			res.end(JSON.stringify({ url: req.url, proto: req.headers['x-forwarded-proto'] }));
		}
	});
	const backendPort = await listen(backend);
	const gateway = createHeatServer({
		origin: 'https://heat.loca.lt',
		backendPort,
		readyToken: 'test-token',
		handler: (req, res) => res.end('frontend')
	});
	const port = await listen(gateway);
	const host = { host: 'heat.loca.lt' };
	try {
		assert.equal((await request(port, '/', { host: 'evil.test' })).status, 421);
		assert.equal((await request(port, '/')).status, 421);
		assert.equal((await request(port, '/api/login', host, 'POST')).status, 403);
		assert.equal((await request(port, '//evil.test', host)).status, 400);
		assert.equal((await request(port, '/', host)).body, 'frontend');
		const login = await request(
			port,
			'/api/login',
			{ ...host, origin: 'https://heat.loca.lt', 'x-forwarded-proto': 'http' },
			'POST'
		);
		assert.equal(login.status, 200);
		assert.equal(JSON.parse(login.body).proto, 'https');
		assert.equal(login.headers['set-cookie'].length, 2);
		assert.equal(JSON.parse((await request(port, '/media/cards/a.webp', host)).body).url,
			'/media/cards/a.webp');
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

if (process.env.HEAT_BUILD_SMOKE === '1') {
	test('actual adapter-node build serves the frontend', async () => {
		process.env.ORIGIN = 'http://127.0.0.1:5173';
		const { handler } = await import('./build/handler.js');
		const gateway = createHeatServer({ origin: process.env.ORIGIN, handler });
		const port = await listen(gateway);
		try {
			const response = await request(port, '/', { host: '127.0.0.1:5173' });
			assert.equal(response.status, 200);
			assert.match(response.body, /<html/i);
		} finally {
			await close(gateway);
		}
	});
}
