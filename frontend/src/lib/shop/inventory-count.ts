import type { CardEntry } from '$lib/types';

// Numero totale di carte possedute: somma le copie di ogni voce.
// Parametri: `cards` voci dell'inventario (una per carta distinta).
// Ritorna: il totale delle copie, 0 se l'elenco è vuoto.
export function totalCopies(cards: Pick<CardEntry, 'copies'>[]): number {
	return cards.reduce((total, card) => total + card.copies, 0);
}
