import { describe, expect, it } from 'vitest';
import type { CardGift } from './card-play-types';
import { reconcileGifts } from './gift-reconcile';

function gift(id: number): CardGift {
	return {
		id,
		race_id: 1,
		card_name: `Carta ${id}`,
		card_path: `cards/${id}.webp`,
		created_at: '2026-10-20T12:00:00'
	};
}

describe('riconciliazione regali', () => {
	it('rimuove un regalo annullato e lascia i nuovi in attesa', () => {
		const first = gift(1);
		const second = gift(2);
		const third = gift(3);
		expect(reconcileGifts([first, second], [second, third])).toEqual({
			visible: [second],
			pending: [third]
		});
	});

	it('uno snapshot vuoto rimuove tutti i regali senza mutare gli input', () => {
		const displayed = Object.freeze([gift(1)]);
		const unseen = Object.freeze([] as CardGift[]);
		expect(reconcileGifts(displayed, unseen)).toEqual({ visible: [], pending: [] });
		expect(displayed).toHaveLength(1);
	});

	it('usa i dati freschi e non trasforma una nuova notifica in una gia mostrata', () => {
		const first = gift(1);
		const fresh = { ...first, card_name: 'Nome aggiornato' };
		expect(reconcileGifts([first], [fresh])).toEqual({ visible: [fresh], pending: [] });
		expect(reconcileGifts([], [first])).toEqual({ visible: [], pending: [first] });
	});
});
