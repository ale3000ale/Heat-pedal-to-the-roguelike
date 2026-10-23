import http from 'node:http';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const hopHeaders = [
	'connection',
	'keep-alive',
	'proxy-authenticate',
	'proxy-authorization',
	'proxy-connection',
	'te',
	'trailer',
	'transfer-encoding',
	'upgrade'
];

/** Copy end-to-end headers, removing connection-nominated and hop-by-hop fields. */
function endToEnd(headers) {
	const result = { ...headers };
	const nominated = String(headers.connection ?? '')
		.split(',')
		.map((name) => name.trim().toLowerCase());
	for (const name of [...hopHeaders, ...nominated]) delete result[name];
	return result;
}

/** Validate an explicit origin; throws for credentials, paths or public plain HTTP. */
export function validateOrigin(value) {
	if (!value || /[\s\\?#@]/.test(value)) throw new Error('Invalid HEAT_PUBLIC_URL');
	const url = new URL(value);
	if (url.pathname !== '/' || url.username || url.password) {
		throw new Error('Specify an origin without path or credentials');
	}
	const local = ['127.0.0.1', 'localhost'].includes(url.hostname) && url.port === '5173';
	if (url.protocol !== 'https:' && !(url.protocol === 'http:' && local)) {
		throw new Error('Public origin requires HTTPS');
	}
	return url;
}

/** Create the loopback gateway. handler is the adapter-node middleware; no DNS targets from input. */
export function createHeatServer({ origin, handler, backendPort = 8000, readyToken = '' }) {
	const publicUrl = validateOrigin(origin);
	const allowed = new Set([publicUrl.host, '127.0.0.1:5173', 'localhost:5173']);
	return http.createServer((req, res) => {
		res.setHeader('X-Content-Type-Options', 'nosniff');
		res.setHeader('Referrer-Policy', 'same-origin');
		if (!allowed.has(req.headers.host?.toLowerCase())) {
			res.writeHead(421).end('Host not allowed');
			return;
		}
		const path = req.url ?? '';
		if (!path.startsWith('/') || path.startsWith('//') || /[\\\r\n]/.test(path)) {
			res.writeHead(400).end('Invalid request path');
			return;
		}
		if (!['GET', 'HEAD', 'OPTIONS'].includes(req.method)) {
			if (req.headers.origin !== publicUrl.origin) {
				res.writeHead(403).end('Origin not allowed');
				return;
			}
		}
		const pathname = path.split('?')[0];
		if (pathname === '/__heat_ready' && req.method === 'GET') {
			res.setHeader('Cache-Control', 'no-store');
			res.setHeader('Content-Type', 'application/json');
			res.end(JSON.stringify({ token: readyToken }));
			return;
		}
		const proxy = ['/api', '/media'].some(
			(prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`)
		);
		if (!proxy) {
			req.headers.host = publicUrl.host;
			for (const name of Object.keys(req.headers)) {
				if (name.startsWith('x-forwarded-') || name === 'forwarded') delete req.headers[name];
			}
			Promise.resolve(handler(req, res)).catch(() => {
				if (!res.headersSent) res.writeHead(500).end('Frontend error');
				else res.destroy();
			});
			return;
		}
		const headers = endToEnd(req.headers);
		for (const name of Object.keys(headers)) {
			if (name.startsWith('x-forwarded-') || name === 'forwarded') delete headers[name];
		}
		headers.host = `127.0.0.1:${backendPort}`;
		headers['x-forwarded-host'] = publicUrl.host;
		headers['x-forwarded-proto'] = publicUrl.protocol.slice(0, -1);
		const upstream = http.request(
			{ hostname: '127.0.0.1', port: backendPort, path, method: req.method, headers },
			(response) => {
				res.writeHead(response.statusCode ?? 502, endToEnd(response.headers));
				res.flushHeaders();
				response.on('error', () => res.destroy());
				response.pipe(res);
			}
		);
		// SSE remains streamed and has no inactivity timeout; no buffering or retries.
		if (!pathname.startsWith('/api/events')) {
			upstream.setTimeout(30000, () => upstream.destroy(new Error('Backend timeout')));
		}
		upstream.on('error', () => {
			if (!res.headersSent) res.writeHead(502).end('Backend unavailable');
			else res.destroy();
		});
		req.on('aborted', () => upstream.destroy());
		res.on('close', () => upstream.destroy());
		req.pipe(upstream);
	});
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
	const origin = validateOrigin(process.env.HEAT_PUBLIC_URL).origin;
	process.env.ORIGIN = origin;
	const { handler } = await import('./build/handler.js');
	const server = createHeatServer({ origin, handler, readyToken: process.env.HEAT_READY_TOKEN });
	server.on('error', (error) => {
		console.error(error);
		process.exitCode = 1;
	});
	server.listen(5173, '127.0.0.1', () => console.log(`Heat gateway: ${origin}`));
	const shutdown = () => {
		server.close(() => process.exit(0));
		setTimeout(() => {
			server.closeAllConnections();
			process.exit(0);
		}, 5000).unref();
	};
	process.once('SIGINT', shutdown);
	process.once('SIGTERM', shutdown);
	if (process.platform === 'win32') process.once('SIGBREAK', shutdown);
}
