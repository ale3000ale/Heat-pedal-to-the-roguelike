// Secondi concessi per annullare un'assegnazione del tasto S (lo stesso valore del backend).
export const UNDO_SECONDS = 60;

/**
 * Secondi rimasti per annullare un'assegnazione.
 *
 * @param deadline Istante limite in millisecondi.
 * @param now Istante attuale in millisecondi.
 * @returns Secondi interi rimasti, arrotondati per eccesso; mai negativi.
 */
export function secondsLeft(deadline: number, now: number): number {
	return Math.max(0, Math.ceil((deadline - now) / 1000));
}
