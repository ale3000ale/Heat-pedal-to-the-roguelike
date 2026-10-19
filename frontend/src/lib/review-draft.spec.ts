import { describe, expect, it } from 'vitest';
import { mergeReviewDraft } from './review-draft';
import type { ReviewInventoryPilot } from './review-counts-types';

function pilots(): ReviewInventoryPilot[] {
	return [
		{
			pilot_id: 1,
			pilot_name: 'Pilota',
			cards: [
				{
					card_name: 'Freno',
					card_path: 'cards/freno.webp',
					total: 2,
					remaining: 0,
					gifted: 1,
					start: 1,
					pool_now: 0,
					pool_max: 2
				}
			]
		}
	];
}

describe('recupero bozza revisione', () => {
	it('recupera i conteggi senza modificare i dati originali', () => {
		const source = pilots();
		const result = mergeReviewDraft(source, {
			pilots: [{ pilot_id: 1, cards: [{ card_name: 'Freno', remaining: 1 }] }]
		});
		expect(result[0].cards[0].remaining).toBe(1);
		expect(source[0].cards[0].remaining).toBe(0);
	});
	it('non nasconde quantità oltre il totale', () => {
		expect(() =>
			mergeReviewDraft(pilots(), {
				pilots: [{ pilot_id: 1, cards: [{ card_name: 'Freno', remaining: 3 }] }]
			})
		).toThrow(RangeError);
	});
	it('rifiuta riferimenti a piloti assenti', () => {
		expect(() =>
			mergeReviewDraft(pilots(), { pilots: [{ pilot_id: 9, cards: [] }] })
		).toThrow(RangeError);
	});
});
