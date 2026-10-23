import { describe, expect, it } from 'vitest';
import type { AdminDeckRead } from './admin-pilot-cards-types';
import { countAdminDeckCopies } from './admin-pilot-cards-view';

function deck(copies: number[]): AdminDeckRead {
	return {
		available: true,
		id: 1,
		version: 1,
		cards: copies.map((count, index) => ({
			name: `Carta ${index}`,
			path: `cards/test-${index}.webp`,
			copies: count
		}))
	};
}


describe('conteggio copie dei contenitori admin', () => {
	it('somma le copie senza contare solo i nomi e senza modificare il contenitore', () => {
		const source = deck([9, 6]);
		const before = structuredClone(source);
		expect(countAdminDeckCopies(source)).toBe(15);
		expect(source).toEqual(before);
	});

	it('conta zero per un contenitore vuoto', () => {
		expect(countAdminDeckCopies(deck([]))).toBe(0);
	});

	it.each([14, 16])('mostra il conteggio %s senza completarlo o limitarlo', (count) => {
		expect(countAdminDeckCopies(deck([count]))).toBe(count);
	});
});
