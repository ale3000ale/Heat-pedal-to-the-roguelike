export type ModalCloseSource = 'button' | 'escape' | 'outside';

/**
 * Decide se il chiamante puo' chiudere il modal oppure deve attendere l'intercettore.
 * @param source X, tasto Escape o clic sullo sfondo.
 * @param closeOnOutside Abilita Escape e sfondo; non disabilita la X.
 * @param onrequestclose Intercettore opzionale, responsabile dell'eventuale conferma.
 * @returns True solo per la chiusura predefinita; false se bloccata o delegata.
 * @throws Propaga gli errori dell'intercettore senza autorizzare la chiusura.
 */
export function shouldCloseModal(
	source: ModalCloseSource,
	closeOnOutside: boolean,
	onrequestclose?: () => void
): boolean {
	if (source !== 'button' && !closeOnOutside) return false;
	if (onrequestclose) {
		onrequestclose();
		return false;
	}
	return true;
}
