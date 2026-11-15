// Cosa succede premendo "Vedi mazzo" nel dettaglio di un campionato.
export type DeckAction = 'hidden' | 'open' | 'choose';

/**
 * Decide se mostrare il pulsante del mazzo e cosa fa.
 * - hidden: campionato chiuso o nessun pilota dell'utente iscritto.
 * - open: un solo pilota iscritto, si va direttamente alla sua pagina.
 * - choose: più piloti iscritti, prima si sceglie il pilota.
 *
 * @param isClosed Vero se il campionato è chiuso.
 * @param enrolledCount Quanti piloti dell'utente sono iscritti a questo campionato.
 * @returns L'azione del pulsante.
 */
export function deckAction(isClosed: boolean, enrolledCount: number): DeckAction {
	if (isClosed || enrolledCount === 0) return 'hidden';
	return enrolledCount === 1 ? 'open' : 'choose';
}
