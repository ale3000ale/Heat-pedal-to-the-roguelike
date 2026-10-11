import { describe, expect, it } from 'vitest';
import { cardSummary, currencyLabel, formatPurchaseDate } from './shop-format';

describe('shop-format', () => {
	it('traduce la valuta', () => {
		expect(currencyLabel('gold')).toBe('oro');
		expect(currencyLabel('sponsor')).toBe('punti sponsor');
	});

	it('riassume le carte con le copie', () => {
		const cards = [
			{ path: 'a.webp', name: 'Turbo', copies: 2 },
			{ path: 'b.webp', name: 'Freni', copies: 1 }
		];
		expect(cardSummary(cards)).toBe('Turbo ×2, Freni ×1');
		expect(cardSummary([])).toBe('nessuna');
	});

	it('lascia invariata una data non valida', () => {
		expect(formatPurchaseDate('non-una-data')).toBe('non-una-data');
	});
});
