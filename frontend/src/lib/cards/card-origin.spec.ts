import { describe, expect, it } from 'vitest';
import { isUploadedCard, uploadsPrefix } from './card-origin';

describe('uploadsPrefix', () => {
	it('costruisce il prefisso del tipo', () => {
		expect(uploadsPrefix('modifiche')).toBe('cards/uploads/modifiche/');
		expect(uploadsPrefix('sponsor')).toBe('cards/uploads/sponsor/');
	});
});

describe('isUploadedCard', () => {
	it('riconosce le carte caricate', () => {
		expect(isUploadedCard({ path: 'cards/uploads/modifiche/turbo.webp' })).toBe(true);
	});

	it('non considera caricate le carte di base', () => {
		expect(isUploadedCard({ path: 'cards/base/modifiche/turbo.webp' })).toBe(false);
	});

	it('con il tipo richiede anche che coincida', () => {
		const card = { path: 'cards/uploads/sponsor/logo.webp' };
		expect(isUploadedCard(card, 'sponsor')).toBe(true);
		expect(isUploadedCard(card, 'modifiche')).toBe(false);
	});
});
