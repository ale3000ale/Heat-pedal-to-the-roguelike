import { describe, expect, it } from 'vitest';
import type { CardEntry } from '$lib/types';
import { isBaseCard } from '../cards/card-origin';
import { excludeCardGroup } from './pool-exclusion';

describe('isBaseCard', () => {
	it('riconosce le carte della cartella di base', () => {
		expect(isBaseCard({ path: 'cards/base/modifiche/freno.webp' } as CardEntry)).toBe(true);
	});

	it('esclude le carte caricate a mano e gli altri percorsi', () => {
		expect(isBaseCard({ path: 'cards/uploads/modifiche/freno.webp' } as CardEntry)).toBe(false);
		expect(isBaseCard({ path: 'cards/starter/freno.webp' } as CardEntry)).toBe(false);
	});
});

describe('excludeCardGroup', () => {
	const cards: CardEntry[] = [
		{ name: 'Base 1', path: 'cards/base/modifiche/base-1.webp', copies: 4 },
		{ name: 'Caricata 1', path: 'cards/uploads/modifiche/caricata-1.webp', copies: 2 },
		{ name: 'Base 2', path: 'cards/base/modifiche/base-2.webp', copies: 1 },
		{ name: 'Caricata 2', path: 'cards/uploads/modifiche/caricata-2.webp', copies: 5 }
	];

	it('azzera solo le carte caricate, lasciando le altre invariate', () => {
		const picks = { 'Base 1': 2, 'Caricata 1': 2, 'Caricata 2': 3 };
		const result = excludeCardGroup(cards, picks, 'caricate');
		expect(result).toEqual({ 'Base 1': 2, 'Caricata 1': 0, 'Caricata 2': 0 });
	});

	it('azzera solo le carte di base, lasciando le caricate invariate', () => {
		const picks = { 'Base 1': 2, 'Base 2': 1, 'Caricata 1': 2 };
		const result = excludeCardGroup(cards, picks, 'base');
		expect(result).toEqual({ 'Base 1': 0, 'Base 2': 0, 'Caricata 1': 2 });
	});

	it("i due comandi si applicano anche uno dopo l'altro", () => {
		let picks: Record<string, number> = { 'Base 1': 2, 'Caricata 1': 2 };
		picks = excludeCardGroup(cards, picks, 'base');
		picks = excludeCardGroup(cards, picks, 'caricate');
		expect(picks).toEqual({
			'Base 1': 0,
			'Base 2': 0,
			'Caricata 1': 0,
			'Caricata 2': 0
		});
	});

	// Le carte del gruppo assenti da picks entrano con 0: non cambia nulla, perché la
	// creazione della pool tiene solo le carte con copie maggiori di zero.
	it('non muta la mappa passata e azzera tutto il gruppo, anche le carte non scelte', () => {
		const picks: Record<string, number> = { 'Base 1': 2 };
		const result = excludeCardGroup(cards, picks, 'caricate');
		expect(picks).toEqual({ 'Base 1': 2 });
		expect(result).toEqual({ 'Base 1': 2, 'Caricata 1': 0, 'Caricata 2': 0 });
	});

	it('non tocca le carte di nessuno dei due gruppi', () => {
		const starter: CardEntry[] = [
			{ name: 'Partenza', path: 'cards/starter/partenza.webp', copies: 3 }
		];
		const picks = { Partenza: 2 };
		expect(excludeCardGroup(starter, picks, 'base')).toEqual({ Partenza: 2 });
		expect(excludeCardGroup(starter, picks, 'caricate')).toEqual({ Partenza: 2 });
	});
});
