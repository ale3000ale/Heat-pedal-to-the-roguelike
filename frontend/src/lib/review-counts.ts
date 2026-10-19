import type { ReviewCounts, ReviewInventoryPilot } from './review-counts-types';

/**
 * Cambia le copie rimaste di una carta, limitandole tra zero e il totale avuto.
 * @param current Copie rimaste attuali.
 * @param total Copie totali avute, inclusi i bonus S.
 * @param delta Incremento o decremento di una copia.
 * @returns Conteggio aggiornato; non modifica gli argomenti.
 * @throws RangeError Se i conteggi non sono interi non negativi o sono incoerenti.
 */
export function adjustRemaining(current: number, total: number, delta: -1 | 1): number {
	if (
		!Number.isInteger(total) ||
		total < 0 ||
		!Number.isInteger(current) ||
		current < 0 ||
		current > total
	) {
		throw new RangeError('Conteggi della carta non validi');
	}
	return Math.min(total, Math.max(0, current + delta));
}

/** Crea una richiesta nuova con tutti i piloti e tutte le carte, senza immagini o massimi client. */
export function toReviewCounts(pilots: ReviewInventoryPilot[]): ReviewCounts {
	return {
		pilots: pilots.map((pilot) => ({
			pilot_id: pilot.pilot_id,
			cards: pilot.cards.map((card) => ({ card_name: card.card_name, remaining: card.remaining }))
		}))
	};
}
