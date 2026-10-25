import type { DraftHost } from './draft-host-context';
import type { DraftStore } from './stores/draft.svelte';
import { requireDraftId } from './draft-validation';

export interface ChampionshipDraftLaunch {
	championshipId: number;
	sessionKey: string | null;
	canManage: boolean;
	closed: boolean;
	raceUnfinished: boolean;
}

/** Apre solo la preparazione nel registro del layout, mai una Race.
 * @param input Contesto corrente della pagina; non e un'autorizzazione server.
 * @param host Registro gia fornito dal layout, non una nuova istanza.
 * @returns Store aperto/riusato oppure null per busy, errore o risposta tardiva.
 * @throws RangeError per ID invalido; Error per guardie locali o recupero necessario.
 * Il chiamante ricontrolla pagina/generazione prima di applicare messaggi dopo await.
 */
export async function openChampionshipDraft(
	input: ChampionshipDraftLaunch,
	host: Pick<DraftHost, 'getState' | 'open'>
): Promise<DraftStore | null> {
	requireDraftId(input.championshipId);
	if (!input.sessionKey) throw new Error('Sessione non disponibile: verifica l accesso.');
	if (!input.canManage) throw new Error('Non hai i permessi per aprire una preparazione.');
	if (input.closed) throw new Error('Il campionato e chiuso.');
	if (input.raceUnfinished) {
		throw new Error(
			"C'è una gara non conclusa (in corso o in revisione): va conclusa prima di crearne un'altra."
		);
	}
	const state = host.getState();
	if (state.contextKey !== input.sessionKey || state.status === 'disposed') {
		throw new Error('Contesto draft cambiato: verifica l accesso.');
	}
	if (state.status === 'blocked')
		throw new Error('Rileggi le preparazioni prima di una nuova apertura.');
	if (state.busy || state.entries.some((entry) => entry.store.busy)) return null;
	return host.open(input.championshipId);
}
