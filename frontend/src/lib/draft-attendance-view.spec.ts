import { describe, expect, it } from 'vitest';
import { draftAttendanceView, MAX_DRAFT_PRESENT } from './draft-attendance-view';
import type { DraftSessionState, DraftSessionStatus } from './draft-session';

function state(): DraftSessionState {
	return {
		status: 'idle', block: null, error: null, completion: null, raceId: null,
		snapshot: {
			id: 1, championship_id: 7, version: 2, phase: 'attendance', first_race: true,
			can_manage: true, my_pilot_ids: [11, 12],
			participants: [
				{ pilot_id: 11, name: 'Anna', present: true },
				{ pilot_id: 12, name: 'Luca', present: false }
			],
			order: [], cards: [], picks: [], preview_slot_id: null, ready: [], current_pilot_id: null
		}
	};
}

describe('vista presenze draft', () => {
	it('divide in presenti e assenti preservando ordine e input', () => {
		const value = state();
		const before = JSON.stringify(value);
		const view = draftAttendanceView(value);
		expect(view.present.map((pilot) => pilot.pilot_id)).toEqual([11]);
		expect(view.absent.map((pilot) => pilot.pilot_id)).toEqual([12]);
		expect(view.canContinue).toBe(true);
		view.present[0].name = 'Altro';
		expect(JSON.stringify(value)).toBe(before);
	});

	it('conta piloti distinti anche con nome uguale e stesso proprietario', () => {
		const value = state();
		value.snapshot!.participants[1] = { pilot_id: 12, name: 'Anna', present: true };
		const view = draftAttendanceView(value);
		expect(view.count).toBe(2);
		expect(view.present.map((pilot) => pilot.pilot_id)).toEqual([11, 12]);
	});

	it('permette di correggere le presenze ma non confermare zero o oltre il limite', () => {
		const value = state();
		value.snapshot!.participants.forEach((pilot) => { pilot.present = false; });
		expect(draftAttendanceView(value)).toMatchObject({ count: 0, canEdit: true, canContinue: false });
		value.snapshot!.participants = Array.from({ length: MAX_DRAFT_PRESENT + 1 }, (_, index) => ({
			pilot_id: index + 1, name: `Pilota ${index + 1}`, present: true
		}));
		expect(draftAttendanceView(value).canContinue).toBe(false);
		value.snapshot!.participants.pop();
		expect(draftAttendanceView(value).canContinue).toBe(true);
	});

	const statuses: DraftSessionStatus[] = ['empty', 'loading', 'writing', 'blocked', 'finished', 'disposed'];
	it.each(statuses)('non abilita comandi in stato %s', (status) => {
		const view = draftAttendanceView({ ...state(), status });
		expect(view.canEdit).toBe(false);
		expect(view.canContinue).toBe(false);
	});

	it('non amplia permessi e non continua in un altra fase o senza snapshot', () => {
		const value = state();
		value.snapshot!.can_manage = false;
		expect(draftAttendanceView(value).canEdit).toBe(false);
		value.snapshot!.can_manage = true;
		value.snapshot!.phase = 'order';
		expect(draftAttendanceView(value).available).toBe(false);
		value.snapshot = null;
		expect(draftAttendanceView(value).present).toEqual([]);
		expect(draftAttendanceView(value).canContinue).toBe(false);
	});

	it('non inventa controlli client su pool, mazzi o prima gara', () => {
		const value = state();
		value.snapshot!.first_race = false;
		expect(draftAttendanceView(value).canContinue).toBe(true);
		expect(value.snapshot!.phase).toBe('attendance');
	});
});
