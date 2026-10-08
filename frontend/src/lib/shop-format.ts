import type { DrawnCard, PurchaseItem } from '$lib/shop-types';

// Etichetta mostrata per la valuta di un pacchetto.
export function currencyLabel(currency: string): string {
	return currency === 'gold' ? 'oro' : 'punti sponsor';
}

// Data e ora di un acquisto in formato italiano; se il testo non è una data valida
// lo restituisce così com'è.
export function formatPurchaseDate(value: string): string {
	const date = new Date(value);
	return Number.isNaN(date.getTime()) ? value : date.toLocaleString('it-IT');
}

// Elenco compatto delle carte ("nome ×copie, ...") oppure "nessuna".
export function cardSummary(cards: DrawnCard[]): string {
	if (cards.length === 0) return 'nessuna';
	return cards.map((card) => `${card.name} ×${card.copies}`).join(', ');
}

// Riga di riepilogo di un acquisto: costo, valuta e data.
export function purchaseLine(purchase: PurchaseItem): string {
	const cost = `${purchase.cost} ${currencyLabel(purchase.currency)}`;
	return `${cost} · ${formatPurchaseDate(purchase.purchased_at)}`;
}
