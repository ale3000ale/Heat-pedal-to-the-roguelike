import type { ShopPack } from '$lib/shop-types';

// Criteri di ordinamento dei pacchetti scelti dal giocatore.
export type PackSort = 'cost-asc' | 'cost-desc' | 'name-asc' | 'name-desc';

// Ordinamento iniziale: dal meno caro al più caro.
export const DEFAULT_PACK_SORT: PackSort = 'cost-asc';

export const PACK_SORT_OPTIONS: { value: PackSort; label: string }[] = [
	{ value: 'cost-asc', label: 'Dal meno caro al più caro' },
	{ value: 'cost-desc', label: 'Dal più caro al meno caro' },
	{ value: 'name-asc', label: 'Alfabetico' },
	{ value: 'name-desc', label: 'Alfabetico inverso' }
];

function compareNames(a: ShopPack, b: ShopPack): number {
	return a.name.localeCompare(b.name, 'it', { sensitivity: 'base' });
}

// Restituisce una copia dei pacchetti ordinata secondo il criterio scelto.
// A parità si ordina per nome e poi per id, così l'ordine è sempre stabile.
// Parametri: packs = pacchetti da ordinare; sort = criterio. Nessun errore previsto.
export function sortPacks(packs: ShopPack[], sort: PackSort): ShopPack[] {
	const direction = sort.endsWith('desc') ? -1 : 1;
	return [...packs].sort((a, b) => {
		const primary = sort.startsWith('cost') ? (a.cost - b.cost) * direction : compareNames(a, b) * direction;
		return primary || compareNames(a, b) || a.id - b.id;
	});
}

// Tiene i pacchetti il cui nome contiene il testo cercato, senza distinguere le maiuscole.
// Un testo vuoto o di soli spazi lascia tutti i pacchetti. Nessun errore previsto.
export function filterPacksByName(packs: ShopPack[], query: string): ShopPack[] {
	const needle = query.trim().toLowerCase();
	if (needle === '') return packs;
	return packs.filter((pack) => pack.name.toLowerCase().includes(needle));
}
