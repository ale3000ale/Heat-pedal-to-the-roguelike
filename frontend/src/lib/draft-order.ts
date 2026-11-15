import type { DraftPilotRead } from './draft-types';
import type { DraftSessionState } from './draft-session';

export interface DraftOrderDraft {
	draftId: number;
	championshipId: number;
	version: number;
	pilotIds: number[];
	baselineIds: number[];
	pilots: DraftPilotRead[];
}

function equal(a: readonly number[], b: readonly number[]): boolean {
	return a.length === b.length && a.every((id, index) => id === b[index]);
}

function permutation(ids: readonly number[], expected: readonly number[]): boolean {
	return (
		expected.length > 0 &&
		ids.length === expected.length &&
		new Set(expected).size === expected.length &&
		new Set(ids).size === ids.length &&
		ids.every((id) => Number.isSafeInteger(id) && id > 0 && expected.includes(id))
	);
}

/** Copia l'ordine server in fase order; null per riferimenti non coerenti o fase diversa.
 * Non genera casualita e non ricalcola l'arrivo precedente. Nessuna mutazione.
 */
export function createDraftOrder(state: DraftSessionState): DraftOrderDraft | null {
	const draft = state.snapshot;
	if (
		!draft ||
		draft.phase !== 'order' ||
		state.status === 'disposed' ||
		state.status === 'finished'
	) {
		return null;
	}
	const pilots = draft.participants.filter((pilot) => pilot.present).map((pilot) => ({ ...pilot }));
	if (
		!permutation(
			draft.order,
			pilots.map((pilot) => pilot.pilot_id)
		)
	)
		return null;
	return {
		draftId: draft.id,
		championshipId: draft.championship_id,
		version: draft.version,
		pilotIds: [...draft.order],
		baselineIds: [...draft.order],
		pilots
	};
}

export function draftOrderChanged(draft: DraftOrderDraft): boolean {
	return !equal(draft.pilotIds, draft.baselineIds);
}

/** Verifica che la bozza appartenga ancora allo snapshot; non concede permessi server. */
export function draftOrderMatches(state: DraftSessionState, draft: DraftOrderDraft): boolean {
	const current = createDraftOrder(state);
	return (
		current !== null &&
		current.draftId === draft.draftId &&
		current.championshipId === draft.championshipId &&
		current.version === draft.version &&
		equal(current.baselineIds, draft.baselineIds) &&
		permutation(draft.pilotIds, current.pilotIds)
	);
}

export function canEditDraftOrder(state: DraftSessionState, draft: DraftOrderDraft): boolean {
	return (
		state.status === 'idle' &&
		state.snapshot?.can_manage === true &&
		draftOrderMatches(state, draft)
	);
}

/** Sposta un pilota in una posizione zero-based e restituisce una nuova bozza.
 * RangeError per pilota, indice o insieme non validi; non scrive sul server.
 */
export function moveDraftOrder(
	draft: DraftOrderDraft,
	pilotId: number,
	index: number
): DraftOrderDraft {
	if (
		!permutation(draft.pilotIds, draft.baselineIds) ||
		!draft.pilotIds.includes(pilotId) ||
		!Number.isSafeInteger(index) ||
		index < 0 ||
		index >= draft.pilotIds.length
	) {
		throw new RangeError('Spostamento ordine non valido');
	}
	const pilotIds = [...draft.pilotIds];
	pilotIds.splice(pilotIds.indexOf(pilotId), 1);
	pilotIds.splice(index, 0, pilotId);
	return {
		...draft,
		pilotIds,
		baselineIds: [...draft.baselineIds],
		pilots: draft.pilots.map((pilot) => ({ ...pilot }))
	};
}

/** Righe indipendenti nell'ordine locale; RangeError per un riferimento sconosciuto. */
export function draftOrderRows(draft: DraftOrderDraft): DraftPilotRead[] {
	return draft.pilotIds.map((id) => {
		const pilot = draft.pilots.find((item) => item.pilot_id === id);
		if (!pilot) throw new RangeError('Pilota assente dalla bozza ordine');
		return { ...pilot };
	});
}

export interface DraftOrderPort {
	state: () => DraftSessionState;
	save: (pilotIds: number[]) => Promise<boolean>;
	start: () => Promise<boolean>;
}

/** Esegue un solo tentativo esplicito: salva se modificato, poi ricontrolla e avvia.
 * accepted indica che l'ordine richiesto e presente nello snapshot server utilizzabile.
 * Una save fallita non chiama start. Nessun retry o rollback fittizio dei due comandi.
 * Errori imprevisti del port si propagano; il port applicativo e lo store versionato.
 */
export async function advanceDraftOrder(draft: DraftOrderDraft, port: DraftOrderPort) {
	if (!canEditDraftOrder(port.state(), draft)) return { accepted: false, started: false };
	if (draftOrderChanged(draft) && !(await port.save([...draft.pilotIds]))) {
		return { accepted: false, started: false };
	}
	const state = port.state();
	const current = createDraftOrder(state);
	if (
		!current ||
		current.draftId !== draft.draftId ||
		current.championshipId !== draft.championshipId ||
		current.version < draft.version ||
		!equal(current.pilotIds, draft.pilotIds) ||
		!canEditDraftOrder(state, current)
	) {
		return { accepted: false, started: false };
	}
	return { accepted: true, started: await port.start() };
}
