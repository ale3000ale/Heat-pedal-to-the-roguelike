import { describe, expect, it } from 'vitest';
import { initialBonus } from './race-bonus-suggestion';

describe('suggerimento punti extra evento', () => {
	it('premia solo le posizioni comprese nel range dell’evento', () => {
		const unsaved = { position: null, bonus_points: 0 };
		expect(initialBonus(unsaved, 1, 3, 2)).toBe(2);
		expect(initialBonus(unsaved, 3, 3, 2)).toBe(2);
		expect(initialBonus(unsaved, 4, 3, 2)).toBe(0);
	});

	it('usa i punti salvati quando la gara ha già una classifica', () => {
		expect(initialBonus({ position: 2, bonus_points: 3 }, 2, 3, 1)).toBe(3);
	});

	it('non propone punti senza un evento che li preveda', () => {
		expect(initialBonus({ position: null, bonus_points: 0 }, 1, 0, 0)).toBe(0);
	});
});
