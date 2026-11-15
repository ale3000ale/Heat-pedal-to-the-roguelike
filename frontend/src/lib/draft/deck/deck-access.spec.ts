import { describe, expect, it } from 'vitest';
import { deckAction } from './deck-access';

describe('deckAction', () => {
	it('nasconde il pulsante in un campionato chiuso', () => {
		expect(deckAction(true, 1)).toBe('hidden');
	});

	it('lo nasconde senza piloti iscritti', () => {
		expect(deckAction(false, 0)).toBe('hidden');
	});

	it('con un solo pilota iscritto apre direttamente il suo mazzo', () => {
		expect(deckAction(false, 1)).toBe('open');
	});

	it('con più piloti iscritti chiede quale scegliere', () => {
		expect(deckAction(false, 3)).toBe('choose');
	});
});
