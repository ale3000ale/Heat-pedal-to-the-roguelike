import type { AdminDeckRead } from './admin-pilot-cards-types';

/**
 * Conta le copie del solo contenitore ricevuto, non le righe o gli altri inventari.
 * @param deck Contenitore restituito e validato dal backend.
 * @returns Somma delle copie, senza correggere mazzi incompleti o eccessivi.
 */
export function countAdminDeckCopies(deck: AdminDeckRead): number {
	return deck.cards.reduce((total, card) => total + card.copies, 0);
}
