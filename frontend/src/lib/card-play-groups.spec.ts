import { describe, expect, it } from 'vitest';
import { countLabel, groupActivePlays } from './card-play-groups';
import type { CardPlay } from './card-play-types';

function play(id: number, name: string, status: CardPlay['status'] = 'giocata'): CardPlay {
	return {
		id,
		card_name: name,
		card_path: `/images/cards/1_${name}.webp`,
		status,
		played_at: '2026-10-12T16:00:00'
	};
}

describe('groupActivePlays', () => {
	it("raggruppa le copie uguali e conserva l'ordine di prima comparsa", () => {
		const groups = groupActivePlays([play(1, 'Turbo'), play(2, 'Freni'), play(3, 'Turbo')]);
		expect(groups.map((g) => [g.name, g.count])).toEqual([
			['Turbo', 2],
			['Freni', 1]
		]);
	});

	it('ignora le giocate annullate e consumate', () => {
		const groups = groupActivePlays([
			play(1, 'Turbo'),
			play(2, 'Turbo', 'annullata'),
			play(3, 'Freni', 'consumata')
		]);
		expect(groups).toHaveLength(1);
		expect(groups[0].count).toBe(1);
	});

	it('non distingue le maiuscole nel nome', () => {
		const groups = groupActivePlays([play(1, 'Turbo'), play(2, 'turbo')]);
		expect(groups).toHaveLength(1);
		expect(groups[0].count).toBe(2);
	});

	it('restituisce un elenco vuoto senza giocate', () => {
		expect(groupActivePlays([])).toEqual([]);
	});
});

describe('countLabel', () => {
	it('mostra x N solo da due copie in su', () => {
		expect(countLabel(1)).toBe('');
		expect(countLabel(2)).toBe('x 2');
		expect(countLabel(10)).toBe('x 10');
	});
});
