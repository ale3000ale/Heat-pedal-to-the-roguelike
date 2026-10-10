import { describe, expect, it } from 'vitest';
import type { ShopPack } from '$lib/shop-types';
import { DEFAULT_PACK_SORT, filterPacksByName, sortPacks } from './shop-sort';

function pack(id: number, name: string, cost: number): ShopPack {
	return {
		id,
		name,
		image_path: 'x.webp',
		currency: 'gold',
		cost,
		modifiche_count: 3,
		sponsor_count: 0,
		filter_enabled: false,
		filter_text: null,
		sold_out: false
	};
}

const packs = [pack(1, 'Beta', 20), pack(2, 'alfa', 10), pack(3, 'Gamma', 10)];
const names = (list: ShopPack[]) => list.map((p) => p.name);

describe('sortPacks', () => {
	it('usa come predefinito dal meno caro al più caro', () => {
		expect(DEFAULT_PACK_SORT).toBe('cost-asc');
	});

	it('ordina per costo crescente, a parità per nome', () => {
		expect(names(sortPacks(packs, 'cost-asc'))).toEqual(['alfa', 'Gamma', 'Beta']);
	});

	it('ordina per costo decrescente, a parità per nome', () => {
		expect(names(sortPacks(packs, 'cost-desc'))).toEqual(['Beta', 'alfa', 'Gamma']);
	});

	it('ordina in modo alfabetico senza distinguere le maiuscole', () => {
		expect(names(sortPacks(packs, 'name-asc'))).toEqual(['alfa', 'Beta', 'Gamma']);
	});

	it('ordina in modo alfabetico inverso', () => {
		expect(names(sortPacks(packs, 'name-desc'))).toEqual(['Gamma', 'Beta', 'alfa']);
	});

	it('non modifica la lista di partenza', () => {
		const original = names(packs);
		sortPacks(packs, 'cost-desc');
		expect(names(packs)).toEqual(original);
	});
});

describe('filterPacksByName', () => {
	it('cerca nel nome senza distinguere le maiuscole', () => {
		expect(names(filterPacksByName(packs, 'AM'))).toEqual(['Gamma']);
	});

	it('con testo vuoto o di soli spazi restituisce tutti i pacchetti', () => {
		expect(filterPacksByName(packs, '   ')).toHaveLength(3);
	});

	it('restituisce una lista vuota se nessun nome corrisponde', () => {
		expect(filterPacksByName(packs, 'zzz')).toEqual([]);
	});
});
