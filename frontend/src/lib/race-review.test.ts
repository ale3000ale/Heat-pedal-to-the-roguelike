import { describe, expect, it } from 'vitest';
import { formatCountdown, secondsLeft } from './race-review-format';

describe('formatCountdown', () => {
	it('formatta i secondi come mm:ss', () => {
		expect(formatCountdown(845)).toBe('14:05');
		expect(formatCountdown(0)).toBe('00:00');
		expect(formatCountdown(900)).toBe('15:00');
	});

	it('tratta valori negativi e non validi come zero', () => {
		expect(formatCountdown(-5)).toBe('00:00');
		expect(formatCountdown(Number.NaN)).toBe('00:00');
	});
});

describe('secondsLeft', () => {
	const now = Date.parse('2026-10-12T20:00:00Z');

	it('calcola i secondi alla scadenza', () => {
		expect(secondsLeft('2026-10-12T20:15:00Z', now)).toBe(900);
		expect(secondsLeft('2026-10-12T20:00:00.400Z', now)).toBe(1);
	});

	it('vale zero con scadenza passata, assente o non valida', () => {
		expect(secondsLeft('2026-10-12T19:59:00Z', now)).toBe(0);
		expect(secondsLeft(null, now)).toBe(0);
		expect(secondsLeft('non-una-data', now)).toBe(0);
	});
});
