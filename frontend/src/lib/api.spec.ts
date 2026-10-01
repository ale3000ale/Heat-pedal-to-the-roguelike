import { describe, expect, it, vi } from 'vitest';
import { api, ApiError } from './api';

// Crea un "fetch finto" che risponde con lo stato e il corpo indicati,
// così i test non hanno bisogno di un backend acceso.
function mockFetch(status: number, body?: unknown) {
	return vi.fn().mockResolvedValue(
		new Response(body === undefined ? null : JSON.stringify(body), {
			status,
			headers: { 'Content-Type': 'application/json' }
		})
	);
}

describe('api', () => {
	// Verifica indirizzo, metodo, cookie e lettura della risposta JSON.
	it('chiama /api con i cookie e restituisce il JSON', async () => {
		const f = mockFetch(200, { id: 1, username: 'mario', role: 'player' });
		const user = await api<{ username: string }>('/auth/me', { fetch: f });
		expect(user.username).toBe('mario');
		expect(f).toHaveBeenCalledWith(
			'/api/auth/me',
			expect.objectContaining({ method: 'GET', credentials: 'same-origin' })
		);
	});

	// Verifica che il corpo venga convertito in JSON con l'intestazione giusta.
	it('invia il corpo come JSON', async () => {
		const f = mockFetch(200, {});
		await api('/auth/login', { method: 'POST', body: { username: 'a', password: 'b' }, fetch: f });
		const init = f.mock.calls[0][1];
		expect(init.body).toBe(JSON.stringify({ username: 'a', password: 'b' }));
		expect(init.headers['Content-Type']).toBe('application/json');
	});

	// Il logout risponde 204 senza corpo: la funzione deve restituire undefined.
	it('restituisce undefined con 204', async () => {
		const f = mockFetch(204);
		expect(await api('/auth/logout', { method: 'POST', fetch: f })).toBeUndefined();
	});

	// Un errore del backend diventa un ApiError con stato e messaggio.
	it('lancia ApiError con il messaggio del server', async () => {
		const f = mockFetch(401, { detail: 'Non autenticato' });
		const error = await api('/auth/me', { fetch: f }).catch((e) => e);
		expect(error).toBeInstanceOf(ApiError);
		expect(error.status).toBe(401);
		expect(error.message).toBe('Non autenticato');
	});

	// Gli errori di validazione (422) hanno un formato a lista: messaggio generico.
	it('gestisce gli errori di validazione 422', async () => {
		const f = mockFetch(422, { detail: [{ msg: 'x' }] });
		const error = await api('/auth/register', { method: 'POST', body: {}, fetch: f }).catch(
			(e) => e
		);
		expect(error.message).toBe('Dati non validi');
	});

	// Se il server è spento, fetch lancia un errore di rete: stato 0.
	it('segnala il server irraggiungibile', async () => {
		const f = vi.fn().mockRejectedValue(new TypeError('fetch failed'));
		const error = await api('/auth/me', { fetch: f }).catch((e) => e);
		expect(error.status).toBe(0);
	});
});
