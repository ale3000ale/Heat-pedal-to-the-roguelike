import { afterEach, describe, expect, it, vi } from 'vitest';
import { AuthStore } from './auth.svelte';

// Costruisce una risposta HTTP finta con stato e corpo JSON.
function reply(status: number, body?: unknown) {
	return new Response(body === undefined ? null : JSON.stringify(body), {
		status,
		headers: { 'Content-Type': 'application/json' }
	});
}

const mario = { id: 2, username: 'mario', role: 'player' };

// Sostituisce fetch globale con una versione finta che restituisce
// le risposte indicate, una per ogni chiamata, nell'ordine.
function fakeFetch(...responses: Response[]) {
	const f = vi.fn();
	responses.forEach((r) => f.mockResolvedValueOnce(r));
	vi.stubGlobal('fetch', f);
	return f;
}

afterEach(() => {
	vi.unstubAllGlobals();
});

describe('AuthStore', () => {
	it('init: imposta l utente se c è una sessione valida', async () => {
		fakeFetch(reply(200, mario));
		const store = new AuthStore();
		await store.init();
		expect(store.user?.username).toBe('mario');
		expect(store.ready).toBe(true);
		expect(store.isAdmin).toBe(false);
	});

	it('init: senza sessione (401) l utente resta null, senza errore', async () => {
		fakeFetch(reply(401, { detail: 'Non autenticato' }));
		const store = new AuthStore();
		await store.init();
		expect(store.user).toBeNull();
		expect(store.error).toBeNull();
		expect(store.ready).toBe(true);
	});

	it('init: se il server è spento segnala l errore', async () => {
		vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('fetch failed')));
		const store = new AuthStore();
		await store.init();
		expect(store.user).toBeNull();
		expect(store.error).toBe('Server non raggiungibile');
		expect(store.ready).toBe(true);
	});

	it('login: dopo il login legge l utente da /auth/me', async () => {
		const f = fakeFetch(reply(200, {}), reply(200, mario));
		const store = new AuthStore();
		await store.login('mario', 'password123');
		expect(store.user?.username).toBe('mario');
		expect(f.mock.calls[0][0]).toBe('/api/auth/login');
		expect(f.mock.calls[1][0]).toBe('/api/auth/me');
	});

	it('login: con credenziali errate lancia un errore e non imposta l utente', async () => {
		fakeFetch(reply(401, { detail: 'Credenziali non valide' }));
		const store = new AuthStore();
		await expect(store.login('mario', 'sbagliata')).rejects.toThrow('Credenziali non valide');
		expect(store.user).toBeNull();
	});

	it('logout: svuota l utente anche se la richiesta fallisce', async () => {
		fakeFetch(reply(200, mario), reply(500, { detail: 'Errore' }));
		const store = new AuthStore();
		await store.init();
		await store.logout().catch(() => {});
		expect(store.user).toBeNull();
	});

	it('isAdmin: vero solo per il ruolo admin', async () => {
		fakeFetch(reply(200, { id: 1, username: 'capo', role: 'admin' }));
		const store = new AuthStore();
		await store.init();
		expect(store.isAdmin).toBe(true);
	});
});
