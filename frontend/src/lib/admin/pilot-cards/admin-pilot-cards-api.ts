import { api } from '../../api';
import type { AdminPilotCardsRead, AdminPilotRead } from './admin-pilot-cards-types';

/** Rifiuta ID non rappresentabili esattamente prima di costruire l'URL. */
function validateId(id: number, label: string): void {
	if (!Number.isSafeInteger(id) || id <= 0) {
		throw new RangeError(`ID ${label} non valido`);
	}
}

/**
 * Legge gli iscritti con username mediante il client API condiviso.
 * @param championshipId Campionato selezionato.
 * @param doFetch Fetch opzionale per i test.
 * @returns Elenco admin, anche vuoto se il backend lo restituisce.
 * @throws RangeError per ID non valido; propaga gli errori API senza retry.
 */
export async function fetchAdminChampionshipPilots(
	championshipId: number,
	doFetch: typeof fetch = fetch
): Promise<AdminPilotRead[]> {
	validateId(championshipId, 'campionato');
	return api<AdminPilotRead[]>(`/admin/championships/${championshipId}/pilots`, {
		fetch: doFetch
	});
}

/**
 * Legge i cinque contenitori senza spostare carte o aprire stream.
 * @param championshipId Campionato selezionato.
 * @param pilotId Pilota iscritto selezionato.
 * @param doFetch Fetch opzionale per i test.
 * @returns Snapshot del contesto richiesto, con versioni e blocchi invariati.
 * @throws RangeError per ID non valido, Error per contesto difforme; propaga ApiError.
 */
export async function fetchAdminPilotCards(
	championshipId: number,
	pilotId: number,
	doFetch: typeof fetch = fetch
): Promise<AdminPilotCardsRead> {
	validateId(championshipId, 'campionato');
	validateId(pilotId, 'pilota');
	const snapshot = await api<AdminPilotCardsRead>(
		`/admin/championships/${championshipId}/pilots/${pilotId}/cards`,
		{ fetch: doFetch }
	);
	if (snapshot?.championship_id !== championshipId || snapshot?.pilot?.pilot_id !== pilotId) {
		throw new Error('La risposta delle carte non corrisponde al campionato e pilota richiesti');
	}
	return snapshot;
}
