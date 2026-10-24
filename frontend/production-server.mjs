import http from 'node:http';
import { isIP } from 'node:net';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const hopHeaders = [
	'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
	'proxy-connection', 'te', 'trailer', 'transfer-encoding', 'upgrade'
];

/** Return true only for canonical RFC1918 IPv4 literals; no DNS resolution. */
export function isLanIPv4(host) {
	if (isIP(host) !== 4) return false;
	const [a, b] = host.split('.').map(Number);
	return a === 10 || (a === 172 && b >= 16 && b <= 31) || (a === 192 && b === 168);
}

/** Remove hop-by-hop and connection-nominated headers before proxying. */
function endToEnd(headers) {
	const result = { ...headers };
	const nominated = String(headers.connection ?? '')
		.split(',').map((name) => name.trim().toLowerCase());
	for (const name of [...hopHeaders, ...nominated]) delete result[name];
	return result;
}

/** Return a validated URL; reject paths, credentials and public plain HTTP. */
export function validateOrigin(value) {
	if (!value || /[\s\\?#@]/.test(value)) throw new Error('Invalid HEAT_PUBLIC_URL');
	const url = new URL(value);
	if (url.pathname !== '/' || url.username || url.password) {
		throw new Error('Specify an origin without path or credentials');
	}
	const local = ['127.0.0.1', 'localhost'].includes(url.hostname);
	const lan = isLanIPv4(url.hostname);
	if (url.protocol !== 'https:' && !(url.protocol === 'http:' && (local || lan) && url.port === '5173')) {
		throw new Error('HTTP requires loopback or private IPv4 on port 5173');
	}
	// WHATWG URL accepts abbreviated/numeric IPv4; require the canonical spelling.
	if (url.protocol === 'http:' && value.replace(/\/$/, '') !== url.origin) {
		throw new Error('HTTP origin must use a canonical host and port');
	}
	return url;
}

/** Return the sole listening IPv4: selected LAN address or loopback for HTTPS. */
export function gatewayHost(origin) {
	const url = validateOrigin(origin);
	return url.protocol === 'http:' && isLanIPv4(url.hostname) ? url.hostname : '127.0.0.1';
}

/** Create gateway with exact Host/Origin checks and a fixed loopback upstream. */
export function createHeatServer({ origin, handler, backendPort = 8000, readyToken = '' }) {
	const publicUrl = validateOrigin(origin);
	const bindHost = gatewayHost(origin);
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
		if (!['GET', 'HEAD', 'OPTIONS'].includes(req.method) && req.headers.origin !== publicUrl.origin) {
			res.writeHead(403).end('Origin not allowed');
			return;
		}
		const pathname = path.split('?')[0];
		if (pathname === '/__heat_ready') {
			const peer = req.socket.remoteAddress?.replace(/^::ffff:/, '');
			if (req.method !== 'GET' || !['127.0.0.1', '::1', bindHost].includes(peer)) {
				res.writeHead(403).end('Readiness is local only');
				return;
			}
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
			Promise.resolve().then(() => handler(req, res)).catch(() => {
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
		// Preserve SSE streaming without buffering, inactivity timeout or retries.
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
	server.listen(5173, gatewayHost(origin), () => console.log(`Heat gateway: ${origin}`));
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
