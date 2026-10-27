import { totalCopies } from '../../shop/inventory-count';
import type { DraftPilotDeckRead } from '../draft-types';
import type { DraftSessionState } from '../draft-session';

/** Deriva solo dati e disponibilita UI dai due DTO, senza mutazioni o rete.
 * Una carta nell'inventario e gia quella restituita dal server: non sottrarre
 * nuovamente il mazzo. can_manage non concede accesso ai mazzi degli altri.
 */
export function draftDeckView(
	state: DraftSessionState,
	pilotId: number | null,
	data: DraftPilotDeckRead | null
) {
	const draft = state.snapshot;
	const visible =
		draft?.phase === 'decks' && state.status !== 'finished' && state.status !== 'disposed';
	const ownPilots =
		visible && draft
			? draft.participants
					.filter((pilot) => pilot.present && draft.my_pilot_ids.includes(pilot.pilot_id))
					.map((pilot) => ({ ...pilot }))
			: [];
	const selected = ownPilots.find((pilot) => pilot.pilot_id === pilotId) ?? ownPilots[0] ?? null;
	const selectedReady = selected !== null && draft?.ready.includes(selected.pilot_id) === true;
	const allOwnReady =
		ownPilots.length > 0 && ownPilots.every((pilot) => draft?.ready.includes(pilot.pilot_id));
	const detail = selected && data?.pilot_id === selected.pilot_id ? data : null;
	const count = detail ? totalCopies(detail.game_deck) : null;
	const current =
		detail !== null &&
		detail.preparation_version === draft?.version &&
		detail.ready === selectedReady;
	const canEdit =
		visible && state.status === 'idle' && selected !== null && current && !selectedReady;
	return {
		visible,
		ownPilots,
		selected,
		selectedReady,
		allOwnReady,
		current,
		count,
		inventory: detail?.inventory.map((card) => ({ ...card })) ?? [],
		gameDeck: detail?.game_deck.map((card) => ({ ...card })) ?? [],
		hasDeck: detail !== null,
		canEdit,
		canAdd: canEdit && count !== null && count < 15,
		canReady:
			canEdit && count !== null && count <= 15 && (draft?.first_race === true || count === 15),
		canUnready: visible && state.status === 'idle' && selected !== null && selectedReady
	};
}
