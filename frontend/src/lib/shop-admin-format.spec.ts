import { describe, expect, it } from 'vitest';
import { errorMessage, packSummary } from './shop-admin-format';

describe('shop-admin-format', () => {
	it('riassume un pacchetto', () => {
		const pack = { cost: 50, currency: 'gold', modifiche_count: 3, sponsor_count: 1 };
		expect(packSummary(pack)).toBe('50 oro · 3 modifiche · 1 sponsor');
	});

	it('ricava il messaggio di un errore', () => {
		expect(errorMessage(new Error('Boom'))).toBe('Boom');
		expect(errorMessage('x')).toBe('Errore sconosciuto');
	});
});
