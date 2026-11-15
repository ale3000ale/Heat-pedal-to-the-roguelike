import type { CardGift } from './card-play-types';

/**
 * Riconcilia il popup con una rilettura riuscita delle notifiche non viste.
 * @param displayed Notifiche effettivamente mostrate nel popup corrente.
 * @param unseen Snapshot REST completo del contesto corrente, non un errore convertito in [].
 * @returns visible contiene solo regali ancora presenti; pending i nuovi non ancora mostrati.
 * Non muta gli input, non segna notifiche viste e non decide come chiudere il popup.
 * Il chiamante deve impedire snapshot obsoleti e gestire gli errori prima di chiamarla.
 */
export function reconcileGifts(displayed: readonly CardGift[], unseen: readonly CardGift[]) {
	const byId = new Map(unseen.map((gift) => [gift.id, gift]));
	const displayedIds = new Set(displayed.map((gift) => gift.id));
	const visible = displayed.flatMap((gift) => {
		const current = byId.get(gift.id);
		return current ? [current] : [];
	});
	const pending = unseen.filter((gift) => !displayedIds.has(gift.id));
	return { visible, pending };
}
