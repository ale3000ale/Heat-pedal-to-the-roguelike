import { describe, expect, it } from 'vitest';
import { AuthStore } from './auth.svelte';
import type { Role } from './types';

function storeWith(role: Role | null): AuthStore {
	const store = new AuthStore();
	store.user = role ? { id: 1, username: 'x', role } : null;
	return store;
}

describe('permessi sulle gare', () => {
	it("l'admin gestisce e corregge le gare", () => {
		const store = storeWith('admin');
		expect(store.isAdmin).toBe(true);
		expect(store.canManageRaces).toBe(true);
		expect(store.canCorrectRaces).toBe(true);
	});

	it('il giudice gestisce le gare ma non le corregge', () => {
		const store = storeWith('judge');
		expect(store.isAdmin).toBe(false);
		expect(store.canManageRaces).toBe(true);
		expect(store.canCorrectRaces).toBe(false);
	});

	it('il giocatore e chi non è loggato non gestiscono le gare', () => {
		for (const store of [storeWith('player'), storeWith(null)]) {
			expect(store.canManageRaces).toBe(false);
			expect(store.canCorrectRaces).toBe(false);
		}
	});
});
