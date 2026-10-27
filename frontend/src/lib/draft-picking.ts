import type { DraftCardSlot, DraftPilotRead } from './draft-types';
import type { DraftSessionState } from './draft-session';

export interface DraftPickingView {
	visible: boolean;
	coherent: boolean;
	ownedTurn: boolean;
	canChoose: boolean;
	/** Tutti i propri piloti presenti hanno gia scelto: resta la sola visione in tempo reale. */
	alreadyChosen: boolean;
	turn: DraftPilotRead | null;
	availableCards: DraftCardSlot[];
	pickedCards: { slot: DraftCardSlot; pilot: DraftPilotRead }[];
	previewSlotId: number | null;
}

/** Deriva copie dei dati pubblici necessari alla scelta, senza consumare carte.
 * Verifica turno e riferimenti delle scelte; non sostituisce l'intero motore server.
 * can_manage non concede il turno: conta la proprieta del pilota corrente.
 */
export function draftPickingView(state: DraftSessionState): DraftPickingView {
	const empty: DraftPickingView = {
		visible: false,
		coherent: false,
		ownedTurn: false,
		canChoose: false,
		alreadyChosen: false,
		turn: null,
		availableCards: [],
		pickedCards: [],
		previewSlotId: null
	};
	const draft = state.snapshot;
	if (
		!draft ||
		draft.phase !== 'picking' ||
		state.status === 'finished' ||
		state.status === 'disposed'
	) {
		return empty;
	}
	const turn =
		draft.participants.find((pilot) => pilot.pilot_id === draft.current_pilot_id) ?? null;
	const availableCards = draft.cards
		.filter((slot) => slot.chosen_by === null)
		.map((slot) => ({ ...slot }));
	let coherent = turn !== null && turn.present && draft.order[draft.picks.length] === turn.pilot_id;
	const pickedCards: DraftPickingView['pickedCards'] = [];
	for (const slotId of draft.picks) {
		const slot = draft.cards.find((item) => item.slot_id === slotId);
		const pilot = draft.participants.find(
			(item) => item.pilot_id === slot?.chosen_by && item.present
		);
		if (!slot || !pilot) {
			coherent = false;
			continue;
		}
		pickedCards.push({ slot: { ...slot }, pilot: { ...pilot } });
	}
	coherent =
		coherent &&
		pickedCards.length === draft.picks.length &&
		draft.cards.filter((slot) => slot.chosen_by !== null).length === draft.picks.length &&
		pickedCards.every((item, index) => item.pilot.pilot_id === draft.order[index]) &&
		(draft.preview_slot_id === null ||
			availableCards.some((slot) => slot.slot_id === draft.preview_slot_id));
	const ownedTurn = coherent && turn !== null && draft.my_pilot_ids.includes(turn.pilot_id);
	const own = draft.participants.filter(
		(pilot) => pilot.present && draft.my_pilot_ids.includes(pilot.pilot_id)
	);
	const alreadyChosen =
		coherent &&
		own.length > 0 &&
		own.every((pilot) => pickedCards.some((item) => item.pilot.pilot_id === pilot.pilot_id));
	return {
		visible: true,
		coherent,
		ownedTurn,
		canChoose: ownedTurn && state.status === 'idle',
		alreadyChosen,
		turn: turn ? { ...turn } : null,
		availableCards,
		pickedCards,
		// Solo indicatore visuale altrui: il DTO server resta intatto anche durante busy.
		previewSlotId: coherent && !ownedTurn ? draft.preview_slot_id : null
	};
}

export interface DraftChoiceProposal {
	draftId: number;
	championshipId: number;
	version: number;
	pilotId: number;
	pilotName: string;
	slotId: number;
	cardName: string;
	cardPath: string;
}

/** Cattura una singola copia disponibile; null se non e il proprio turno utilizzabile. */
export function proposeDraftChoice(
	state: DraftSessionState,
	slotId: number
): DraftChoiceProposal | null {
	const view = draftPickingView(state);
	const slot = view.availableCards.find((item) => item.slot_id === slotId);
	if (!view.canChoose || !view.turn || !slot || !state.snapshot) return null;
	return {
		draftId: state.snapshot.id,
		championshipId: state.snapshot.championship_id,
		version: state.snapshot.version,
		pilotId: view.turn.pilot_id,
		pilotName: view.turn.name,
		slotId,
		cardName: slot.name,
		cardPath: slot.path
	};
}

/** Ricontrolla contesto, versione, turno e copia prima di inviare choice. */
export function canConfirmDraftChoice(
	state: DraftSessionState,
	proposal: DraftChoiceProposal | null
): boolean {
	if (!proposal) return false;
	const current = proposeDraftChoice(state, proposal.slotId);
	return (
		current !== null &&
		current.draftId === proposal.draftId &&
		current.championshipId === proposal.championshipId &&
		current.version === proposal.version &&
		current.pilotId === proposal.pilotId &&
		current.pilotName === proposal.pilotName &&
		current.cardName === proposal.cardName &&
		current.cardPath === proposal.cardPath
	);
}

/** Produce soltanto il payload preview consentito; null significa nessuna scrittura.
 * Il payload {slot_id: null} revoca l'anteprima ed e distinto dal ritorno null.
 */
export function proposeDraftPreview(state: DraftSessionState, slotId: number | null) {
	const view = draftPickingView(state);
	if (
		!view.canChoose ||
		(slotId !== null && !view.availableCards.some((slot) => slot.slot_id === slotId))
	) {
		return null;
	}
	return { slot_id: slotId };
}
