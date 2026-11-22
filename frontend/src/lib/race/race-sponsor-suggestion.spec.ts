import { describe, expect, it } from 'vitest';
import { initialSponsor } from './race-sponsor-suggestion';

describe('punto sponsor iniziale', () => {
	it('usa i punti salvati per un risultato già registrato', () => {
		expect(initialSponsor({ position: 2, sponsor_points: 3, suggested_sponsor_points: 1 })).toBe(3);
	});

	it('usa il suggerimento dei tasti S per un pilota non ancora classificato', () => {
		expect(initialSponsor({ position: null, sponsor_points: 0, suggested_sponsor_points: 2 })).toBe(
			2
		);
	});

	it('parte da zero quando non ci sono assegnazioni', () => {
		expect(initialSponsor({ position: null, sponsor_points: 0, suggested_sponsor_points: 0 })).toBe(
			0
		);
	});
});
