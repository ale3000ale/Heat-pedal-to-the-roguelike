import type { ReviewCounts, ReviewInventoryPilot } from './review-counts-types';

/**
 * Applica una bozza a una copia dell'inventario ricevuto dal server.
 * @param pilots Inventari correnti, non modificati.
 * @param draft Conteggi salvati, oppure null.
 * @returns Nuovi inventari con le quantità della bozza.
 * @throws RangeError Per riferimenti non presenti o quantità fuori dai limiti.
 */
export function mergeReviewDraft(
	pilots: ReviewInventoryPilot[],
	draft: ReviewCounts | null
): ReviewInventoryPilot[] {
	const result = pilots.map((p) => ({ ...p, cards: p.cards.map((c) => ({ ...c })) }));
	for (const saved of draft?.pilots ?? []) {
		const pilot = result.find((p) => p.pilot_id === saved.pilot_id);
		if (!pilot) throw new RangeError('La bozza contiene un pilota non presente');
		for (const item of saved.cards) {
			const key = item.card_name.trim().toLowerCase();
			const card = pilot.cards.find((c) => c.card_name.trim().toLowerCase() === key);
			if (!card || !Number.isInteger(item.remaining) || item.remaining < 0 || item.remaining > card.total) {
				throw new RangeError('La bozza contiene quantità non valide: ricontrolla i piloti');
			}
			card.remaining = item.remaining;
		}
	}
	return result;
}
