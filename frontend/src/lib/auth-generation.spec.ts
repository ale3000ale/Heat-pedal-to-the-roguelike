import { afterEach, describe, expect, it, vi } from 'vitest';
import { AuthStore } from './auth.svelte';

const player = { id: 9, username: 'anna', role: 'player' as const };
function reply(status: number, body?: unknown): Response {
	return new Response(body === undefined ? null : JSON.stringify(body), {
		status, headers: { 'Content-Type': 'application/json' }
	});
}
function deferred<T>() {
	let resolve!: (value: T) => void;
	const promise = new Promise<T>((done) => { resolve = done; });
	return { promise, resolve };
}
afterEach(() => vi.unstubAllGlobals());

describe('generazione autenticata locale', () => {
	it('non produce chiavi prima del recupero iniziale o senza utente', async () => {
		const store = new AuthStore();
		expect(store.sessionKey).toBeNull();
		vi.stubGlobal('fetch', vi.fn().mockResolvedValue(reply(401, { detail: 'Non autenticato' })));
		await store.init();
		expect(store.ready).toBe(true);
		expect(store.authenticating).toBe(false);
		expect(store.sessionKey).toBeNull();
	});

	it('invalida subito durante login e distingue un nuovo accesso dello stesso utente', async () => {
		const store = new AuthStore();
		store.ready = true;
		store.user = { ...player };
		const previous = store.sessionKey;
		const pending = deferred<Response>();
		vi.stubGlobal('fetch', vi.fn().mockReturnValueOnce(pending.promise).mockResolvedValueOnce(reply(200, player)));
		const login = store.login('anna', 'example-only');
		expect(store.authenticating).toBe(true);
		expect(store.sessionKey).toBeNull();
		pending.resolve(reply(204));
		await login;
		expect(store.user?.id).toBe(9);
		expect(store.authenticating).toBe(false);
		expect(store.sessionKey).not.toBe(previous);
	});

	it('include il ruolo e reagisce anche allo svuotamento diretto usato da SSE', () => {
		const store = new AuthStore();
		store.ready = true;
		store.user = { ...player };
		const previous = store.sessionKey;
		store.user = { ...player, role: 'judge' };
		expect(store.sessionKey).not.toBe(previous);
		store.user = null;
		expect(store.sessionKey).toBeNull();
	});

	it('libera i metadati e conserva il logout anche su errore', async () => {
		const store = new AuthStore();
		store.ready = true;
		store.user = { ...player };
		vi.stubGlobal('fetch', vi.fn().mockResolvedValue(reply(500, { detail: 'Errore' })));
		const logout = store.logout();
		expect(store.sessionKey).toBeNull();
		await expect(logout).rejects.toThrow();
		expect(store.user).toBeNull();
		expect(store.authenticating).toBe(false);
	});

	it('non lascia una transizione aperta dopo registrazione rifiutata', async () => {
		const store = new AuthStore();
		vi.stubGlobal('fetch', vi.fn().mockResolvedValue(reply(422, { detail: 'Dati non validi' })));
		await expect(store.register('anna', 'example-only')).rejects.toThrow();
		expect(store.authenticating).toBe(false);
		expect(store.user).toBeNull();
	});
});
