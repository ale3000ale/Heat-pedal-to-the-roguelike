import { api } from '../../api';
import type { AdminPilotCardsSave } from './admin-pilot-cards-save-types';
import type { AdminPilotCardsRead } from './admin-pilot-cards-types';

/** Risposta non utilizzabile: non implica rollback e non autorizza retry automatici. */
export class AdminCardSaveResponseError extends Error {
	constructor() {
		super(
			'Risposta di salvataggio inattesa: il server potrebbe avere applicato le modifiche. Verificare lo stato prima di riprovare.'
		);
		this.name = 'AdminCardSaveResponseError';
	}
}

/** Rifiuta identificatori non rappresentabili esattamente prima della rete. */
function validateId(id: number, label: string): void {
	if (!Number.isSafeInteger(id) || id <= 0) {
		throw new RangeError(`ID ${label} non valido`);
	}
}

/**
 * Invia una sola PUT attraverso il trasporto condiviso, senza gestire la bozza UI.
 * @param championshipId Campionato selezionato.
 * @param pilotId Pilota iscritto selezionato.
 * @param request Versioni iniziali e registro ordinato dei trasferimenti.
 * @param doFetch Fetch opzionale per test senza rete reale.
 * @returns Snapshot restituito dal backend per lo stesso campionato e pilota.
 * @throws RangeError per ID invalidi; propaga ApiError, inclusi conflitti e rete.
 * @throws AdminCardSaveResponseError se la risposta non identifica il contesto atteso.
 * Non valida il successo tramite una GET, non ritenta e non modifica gli input.
 * La validazione autorevole di versioni, movimenti e permessi resta nel backend.
 */
export async function saveAdminPilotCards(
	championshipId: number,
	pilotId: number,
	request: AdminPilotCardsSave,
	doFetch: typeof fetch = fetch
): Promise<AdminPilotCardsRead> {
	validateId(championshipId, 'campionato');
	validateId(pilotId, 'pilota');
	const snapshot = await api<AdminPilotCardsRead>(
		`/admin/championships/${championshipId}/pilots/${pilotId}/cards`,
		{ method: 'PUT', body: request, fetch: doFetch }
	);
	if (snapshot?.championship_id !== championshipId || snapshot?.pilot?.pilot_id !== pilotId) {
		throw new AdminCardSaveResponseError();
	}
	return snapshot;
}
