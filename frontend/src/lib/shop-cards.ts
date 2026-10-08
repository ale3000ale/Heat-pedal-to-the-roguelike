import type { DrawnCard, PurchaseResult } from '$lib/shop-types';

// Sezione del negozio a cui appartiene una carta uscita.
export type CardSection = 'modifiche' | 'sponsor';

// Carta uscita con la sezione di provenienza.
export interface RevealedCard {
	card: DrawnCard;
	section: CardSection;
}

// Ordine di apertura di un pacchetto: prima tutte le modifiche, poi gli sponsor,
// mantenendo l'ordine ricevuto dal backend dentro ogni sezione.
// Non modifica l'oggetto ricevuto.
export function revealOrder(
	result: Pick<PurchaseResult, 'cards_modifiche' | 'cards_sponsor'>
): RevealedCard[] {
	return [
		...result.cards_modifiche.map((card): RevealedCard => ({ card, section: 'modifiche' })),
		...result.cards_sponsor.map((card): RevealedCard => ({ card, section: 'sponsor' }))
	];
}

// URL dell'immagine di un pacchetto: image_path è relativo a /media/pack.
export function packImageUrl(imagePath: string): string {
	return `/media/pack/${imagePath}`;
}
