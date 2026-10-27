import type { DraftSessionState } from '../draft-session';

// Corrisponde al limite esistente di confirm_attendance/MAX_RACE_PILOTS.
export const MAX_DRAFT_PRESENT = 12;

/** Deriva copie degli elenchi e disponibilita tecnica, senza mutare o salvare dati.
 * Conta piloti, non account o nomi. Non legge mazzi/pool e non sceglie la fase successiva.
 * Le autorizzazioni e tutti i vincoli vengono comunque ricontrollati dal server.
 */
export function draftAttendanceView(state: DraftSessionState) {
	const draft = state.snapshot;
	const participants = draft?.participants ?? [];
	const present = participants.filter((pilot) => pilot.present).map((pilot) => ({ ...pilot }));
	const absent = participants.filter((pilot) => !pilot.present).map((pilot) => ({ ...pilot }));
	const terminal = state.status === 'finished' || state.status === 'disposed';
	const available = draft?.phase === 'attendance' && !terminal;
	const canEdit = available && state.status === 'idle' && draft?.can_manage === true;
	return {
		available,
		present,
		absent,
		count: present.length,
		canEdit,
		canContinue: canEdit && present.length >= 1 && present.length <= MAX_DRAFT_PRESENT
	};
}
