import type { Pilot } from './types';

/**
 * Sceglie i piloti dell'utente che si possono iscrivere a un campionato.
 * Servono un team e nessun campionato attivo: `Pilot.championship` è valorizzato per il
 * campionato attivo a cui il pilota è già iscritto (compreso quello aperto in pagina).
 *
 * @param pilots Piloti dell'utente loggato, come li restituisce GET /pilots.
 * @returns I piloti iscrivibili, nell'ordine ricevuto.
 */
export function enrollablePilots(pilots: Pilot[]): Pilot[] {
	return pilots.filter((pilot) => pilot.team_id !== null && !pilot.championship);
}

/**
 * Decide se mostrare il pulsante "Iscrivi un pilota" nel dettaglio di un campionato.
 * Il pulsante c'è solo se il campionato è attivo e l'utente non ha ancora piloti iscritti.
 *
 * @param isClosed Vero se il campionato è chiuso.
 * @param enrolledCount Quanti piloti dell'utente sono già iscritti a questo campionato.
 * @returns Vero se il pulsante va mostrato.
 */
export function canShowEnroll(isClosed: boolean, enrolledCount: number): boolean {
	return !isClosed && enrolledCount === 0;
}
