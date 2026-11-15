import { describe, expect, it } from 'vitest';
import { cardDelayMs, initialPhase, nextPhase } from './pack-reveal-phases';

describe('nextPhase', () => {
	it('segue la sequenza busta, strappo, scorrimento, carte', () => {
		expect(nextPhase('sealed')).toBe('tearing');
		expect(nextPhase('tearing')).toBe('sliding');
		expect(nextPhase('sliding')).toBe('cards');
	});

	it('resta sulle carte alla fine', () => {
		expect(nextPhase('cards')).toBe('cards');
	});
});

describe('initialPhase', () => {
	it('parte dalla busta chiusa', () => {
		expect(initialPhase(false)).toBe('sealed');
	});

	it('salta alle carte con il movimento ridotto', () => {
		expect(initialPhase(true)).toBe('cards');
	});
});

describe('cardDelayMs', () => {
	it('cresce con la posizione', () => {
		expect(cardDelayMs(0)).toBe(0);
		expect(cardDelayMs(2)).toBe(240);
	});

	it('ha un tetto massimo', () => {
		expect(cardDelayMs(100)).toBe(1200);
	});

	it('non va sotto zero', () => {
		expect(cardDelayMs(-3)).toBe(0);
	});
});
