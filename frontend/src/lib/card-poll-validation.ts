// Limiti dell'intervallo di controllo delle notifiche, uguali a quelli del backend.
export const CARD_POLL_MIN = 1;
export const CARD_POLL_MAX = 10;
export const CARD_POLL_DEFAULT = 5;

// Controlla il testo scritto nel campo dell'intervallo.
// Parametri: `text` valore digitato dall'admin.
// Ritorna: `{ seconds }` se valido, altrimenti `{ error }` con il messaggio da mostrare.
export function parseCardPoll(text: string): { seconds: number } | { error: string } {
	const trimmed = text.trim();
	if (!/^\d+$/.test(trimmed)) return { error: 'Scrivi un numero intero di secondi' };
	const seconds = Number(trimmed);
	if (seconds < CARD_POLL_MIN || seconds > CARD_POLL_MAX) {
		return { error: `L'intervallo va da ${CARD_POLL_MIN} a ${CARD_POLL_MAX} secondi` };
	}
	return { seconds };
}
