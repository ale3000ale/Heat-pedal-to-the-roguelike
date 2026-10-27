import { describe, expect, it } from 'vitest';
import { totalCopies } from './inventory-count';

describe('totalCopies', () => {
	it('ritorna 0 per un elenco vuoto', () => {
		expect(totalCopies([])).toBe(0);
	});

	it('somma le copie di tutte le voci', () => {
		expect(totalCopies([{ copies: 2 }, { copies: 3 }, { copies: 1 }])).toBe(6);
	});
});
