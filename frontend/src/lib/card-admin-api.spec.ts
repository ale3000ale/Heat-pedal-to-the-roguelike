import { describe, expect, it, vi } from 'vitest';
import { ApiError } from './api';
import { deleteCard, uploadCard } from './card-admin-api';

function jsonResponse(status: number, body: unknown): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { 'Content-Type': 'application/json' }
	});
}

const image = new Blob(['x'], { type: 'image/webp' });

describe('uploadCard', () => {
	it('invia l\'immagine nel corpo e i dati nell\'indirizzo', async () => {
		const created = { name: 'Turbo X', path: 'cards/uploads/modifiche/turbo-x.webp', copies: 3, kind: 'modifiche' };
		const fetchMock = vi.fn().mockResolvedValue(jsonResponse(201, created));
		const result = await uploadCard('modifiche', 'Turbo X', 3, image, fetchMock);
		expect(result).toEqual(created);
		const [url, init] = fetchMock.mock.calls[0];
		expect(url).toBe('/api/admin/cards?kind=modifiche&name=Turbo+X&copies=3');
		expect(init.method).toBe('POST');
		expect(init.body).toBe(image);
		expect(init.headers['Content-Type']).toBe('image/webp');
	});

	it('lancia ApiError col messaggio del backend', async () => {
		const fetchMock = vi
			.fn()
			.mockResolvedValue(jsonResponse(409, { detail: 'Esiste già una carta con questo nome' }));
		const error = await uploadCard('sponsor', 'Logo', 1, image, fetchMock).catch((e) => e);
		expect(error).toBeInstanceOf(ApiError);
		expect(error.status).toBe(409);
		expect(error.message).toBe('Esiste già una carta con questo nome');
	});

	it('usa un messaggio generico se il corpo non è JSON', async () => {
		const fetchMock = vi.fn().mockResolvedValue(new Response('boom', { status: 413 }));
		const error = await uploadCard('sponsor', 'Logo', 1, image, fetchMock).catch((e) => e);
		expect(error.message).toBe('Errore 413');
	});

	it('segnala il server non raggiungibile con stato 0', async () => {
		const fetchMock = vi.fn().mockRejectedValue(new TypeError('network'));
		const error = await uploadCard('sponsor', 'Logo', 1, image, fetchMock).catch((e) => e);
		expect(error).toBeInstanceOf(ApiError);
		expect(error.status).toBe(0);
	});
});

describe('deleteCard', () => {
	it('chiama DELETE con tipo e nome', async () => {
		const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, { removed_files: ['cards/uploads/modifiche/a.webp'] }));
		vi.stubGlobal('fetch', fetchMock);
		try {
			const result = await deleteCard('modifiche', 'Turbo X');
			expect(result.removed_files).toHaveLength(1);
			const [url, init] = fetchMock.mock.calls[0];
			expect(url).toBe('/api/admin/cards?kind=modifiche&name=Turbo+X');
			expect(init.method).toBe('DELETE');
		} finally {
			vi.unstubAllGlobals();
		}
	});
});
