import { describe, expect, it, vi } from 'vitest';
import { fetchSiteQr, isLocalOnlyUrl } from './site-qr';

function reply(body: unknown, status = 200): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { 'Content-Type': 'application/json' }
	});
}

describe('fetchSiteQr', () => {
	it('chiede il QR al backend con i cookie di sessione', async () => {
		const fetchMock = vi
			.fn()
			.mockResolvedValue(
				reply({ url: 'http://192.168.1.50:5173', image: 'data:image/png;base64,AAA' })
			);
		const result = await fetchSiteQr(fetchMock);
		expect(result.url).toBe('http://192.168.1.50:5173');
		expect(result.image).toBe('data:image/png;base64,AAA');
		expect(fetchMock).toHaveBeenCalledWith(
			'/api/site/qr',
			expect.objectContaining({ method: 'GET', credentials: 'same-origin' })
		);
	});

	it('propaga il messaggio di errore del backend', async () => {
		const fetchMock = vi.fn().mockResolvedValue(reply({ detail: 'Non autenticato' }, 401));
		await expect(fetchSiteQr(fetchMock)).rejects.toThrow('Non autenticato');
	});
});

describe('isLocalOnlyUrl', () => {
	it.each([
		['http://localhost:5173', true],
		['http://127.0.0.1:5173', true],
		['http://[::1]:5173', true],
		['http://192.168.1.50:5173', false],
		['https://heat.example', false],
		['non un url', false]
	])('%s -> %s', (value, expected) => {
		expect(isLocalOnlyUrl(value)).toBe(expected);
	});
});
