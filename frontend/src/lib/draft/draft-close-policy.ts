import type { DraftSessionState } from './draft-session';

export interface DraftCancellationProposal {
	draftId: number;
}

/** Calcola solo la disponibilita UI della X, senza autorizzare scritture server.
 * Lo stato deve provenire dallo store. Nessuna mutazione o richiesta di rete.
 * READY blocca il creatore solo se tutti i suoi piloti presenti sono pronti,
 * come cancel_preparation; un creatore senza presenti non e pronto per vacuita.
 */
export function draftClosePolicy(state: DraftSessionState) {
	const draft = state.snapshot;
	const ownPresent =
		draft?.participants.filter(
			(pilot) => pilot.present && draft.my_pilot_ids.includes(pilot.pilot_id)
		) ?? [];
	const readyLocked =
		ownPresent.length > 0 && ownPresent.every((pilot) => draft?.ready.includes(pilot.pilot_id));
	const terminal = state.status === 'finished' || state.status === 'disposed';
	const showClose = draft?.can_manage === true && !terminal && !readyLocked;
	return { showClose, readyLocked, canRequest: showClose && state.status === 'idle' };
}

/** Fissa la preparazione della conferma solo da uno snapshot utilizzabile.
 * La versione non e legata alla proposta: il controller invia quella corrente al clic,
 * cosi preview o scelte degli altri giocatori non chiudono la conferma.
 */
export function proposeDraftCancellation(
	state: DraftSessionState
): DraftCancellationProposal | null {
	if (!draftClosePolicy(state).canRequest || !state.snapshot) return null;
	return { draftId: state.snapshot.id };
}

/** Vero quando la conferma non potra piu valere: altra draft, X tolta o stato bloccato.
 * Letture o scritture in corso sospendono la conferma senza farla scadere.
 */
export function draftCancellationExpired(
	state: DraftSessionState,
	proposal: DraftCancellationProposal | null
): boolean {
	return (
		proposal === null ||
		state.status === 'blocked' ||
		!draftClosePolicy(state).showClose ||
		state.snapshot?.id !== proposal.draftId
	);
}

/** Ricontrolla lo stato al clic: conferme scadute o stato non idle non inviano cancel. */
export function canConfirmDraftCancellation(
	state: DraftSessionState,
	proposal: DraftCancellationProposal | null
): boolean {
	return !draftCancellationExpired(state, proposal) && draftClosePolicy(state).canRequest;
}
