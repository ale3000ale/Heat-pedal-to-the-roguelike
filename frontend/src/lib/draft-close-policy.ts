import type { DraftSessionState } from './draft-session';

export interface DraftCancellationProposal {
	draftId: number;
	version: number;
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

/** Fissa ID/versione della conferma solo da uno snapshot utilizzabile. */
export function proposeDraftCancellation(
	state: DraftSessionState
): DraftCancellationProposal | null {
	if (!draftClosePolicy(state).canRequest || !state.snapshot) return null;
	return { draftId: state.snapshot.id, version: state.snapshot.version };
}

/** Ricontrolla lo stato al clic: conferme obsolete non possono inviare cancel. */
export function canConfirmDraftCancellation(
	state: DraftSessionState,
	proposal: DraftCancellationProposal | null
): boolean {
	return (
		proposal !== null &&
		draftClosePolicy(state).canRequest &&
		state.snapshot?.id === proposal.draftId &&
		state.snapshot.version === proposal.version
	);
}
