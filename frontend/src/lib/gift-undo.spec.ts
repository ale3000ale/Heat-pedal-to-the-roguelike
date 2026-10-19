import { describe, expect, it } from 'vitest';
import { secondsLeft, UNDO_SECONDS } from './gift-undo';

describe('secondsLeft', () => {
	it("subito dopo l'assegnazione restano tutti i secondi", () => {
		expect(secondsLeft(1000 + UNDO_SECONDS * 1000, 1000)).toBe(UNDO_SECONDS);
	});

	it('arrotonda per eccesso i secondi parziali', () => {
		expect(secondsLeft(10_000, 9_001)).toBe(1);
	});

	it('non scende mai sotto zero', () => {
		expect(secondsLeft(10_000, 20_000)).toBe(0);
	});
});
