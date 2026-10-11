import { describe, expect, it } from 'vitest';
import { packImageUrl, revealOrder } from './shop-cards';
import type { DrawnCard } from './shop-types';

function card(name: string, copies = 1): DrawnCard {
	return { name, path: `cards/${name}.webp`, copies };
}

describe('revealOrder', () => {
	it('mostra prima le modifiche e poi gli sponsor', () => {
		const result = revealOrder({
			cards_modifiche: [card('Turbo'), card('Freni')],
			cards_sponsor: [card('Sponsor A')]
		});
		expect(result.map((r) => [r.card.name, r.section])).toEqual([
			['Turbo', 'modifiche'],
			['Freni', 'modifiche'],
			['Sponsor A', 'sponsor']
		]);
	});

	it('regge un pacchetto senza sponsor o senza modifiche', () => {
		expect(revealOrder({ cards_modifiche: [], cards_sponsor: [] })).toEqual([]);
		const onlySponsor = revealOrder({ cards_modifiche: [], cards_sponsor: [card('S')] });
		expect(onlySponsor.map((r) => r.section)).toEqual(['sponsor']);
	});

	it('non modifica i dati ricevuti', () => {
		const input = { cards_modifiche: [card('A')], cards_sponsor: [card('B')] };
		revealOrder(input);
		expect(input.cards_modifiche).toHaveLength(1);
		expect(input.cards_sponsor).toHaveLength(1);
	});
});

describe('packImageUrl', () => {
	it("costruisce l'URL sotto /media/pack", () => {
		expect(packImageUrl('illustration/turbo.webp')).toBe('/media/pack/illustration/turbo.webp');
	});
});
