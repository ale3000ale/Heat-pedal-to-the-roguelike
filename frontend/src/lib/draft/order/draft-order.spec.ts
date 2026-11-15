import { describe, expect, it, vi } from 'vitest';
import {
	advanceDraftOrder,
	canEditDraftOrder,
	createDraftOrder,
	draftOrderChanged,
	draftOrderMatches,
	draftOrderRows,
	moveDraftOrder
} from './draft-order';
import type { DraftSessionState } from '../draft-session';

function state(): DraftSessionState {
	return {
		status: 'idle',
		block: null,
		error: null,
		completion: null,
		raceId: null,
		snapshot: {
			id: 1,
			championship_id: 7,
			version: 2,
			phase: 'order',
			first_race: true,
			can_manage: true,
			my_pilot_ids: [11],
			participants: [
				{ pilot_id: 11, name: 'Anna', present: true },
				{ pilot_id: 12, name: 'Luca', present: true },
				{ pilot_id: 13, name: 'Assente', present: false }
			],
			order: [12, 11],
			cards: [],
			picks: [],
			preview_slot_id: null,
			ready: [],
			current_pilot_id: null
		}
	};
}

function setup() {
	const current = state();
	const save = vi.fn<(ids: number[]) => Promise<boolean>>().mockImplementation(async (ids) => {
		current.snapshot!.order = [...ids];
		current.snapshot!.version += 1;
		return true;
	});
	const start = vi.fn<() => Promise<boolean>>().mockResolvedValue(true);
	return { current, save, start, port: { state: () => current, save, start } };
}

describe('bozza ordine draft', () => {
	it('conserva l ordine server, non include assenti e non muta lo snapshot', () => {
		const current = state();
		const before = JSON.stringify(current);
		const draft = createDraftOrder(current)!;
		expect(draft.pilotIds).toEqual([12, 11]);
		expect(draftOrderRows(draft).map((pilot) => pilot.name)).toEqual(['Luca', 'Anna']);
		const moved = moveDraftOrder(draft, 11, 0);
		expect(moved.pilotIds).toEqual([11, 12]);
		expect(draftOrderChanged(moved)).toBe(true);
		expect(draft.pilotIds).toEqual([12, 11]);
		expect(JSON.stringify(current)).toBe(before);
	});

	it('rifiuta ordini incompleti, duplicati o con assenti senza ripararli', () => {
		for (const order of [[11], [11, 11], [11, 13], []]) {
			const current = state();
			current.snapshot!.order = order;
			expect(createDraftOrder(current)).toBeNull();
		}
	});

	it('rifiuta spostamenti fuori indice o con piloti sconosciuti', () => {
		const draft = createDraftOrder(state())!;
		for (const index of [-1, 2, 0.5, NaN]) {
			expect(() => moveDraftOrder(draft, 11, index)).toThrow(RangeError);
		}
		expect(() => moveDraftOrder(draft, 13, 0)).toThrow(RangeError);
	});

	it('invalida su versione o baseline cambiata senza sovrascrivere la bozza', () => {
		const current = state();
		const draft = moveDraftOrder(createDraftOrder(current)!, 11, 0);
		current.snapshot!.version = 3;
		expect(draftOrderMatches(current, draft)).toBe(false);
		current.snapshot!.version = 2;
		current.snapshot!.order = [11, 12];
		expect(draftOrderMatches(current, draft)).toBe(false);
		expect(draft.baselineIds).toEqual([12, 11]);
	});

	it('non abilita gestori assenti o operazioni in corso', () => {
		const current = state();
		const draft = createDraftOrder(current)!;
		current.snapshot!.can_manage = false;
		expect(canEditDraftOrder(current, draft)).toBe(false);
		current.snapshot!.can_manage = true;
		current.status = 'writing';
		expect(canEditDraftOrder(current, draft)).toBe(false);
	});
});

describe('salvataggio prima dell avvio', () => {
	it('avvia direttamente se l ordine non e modificato', async () => {
		const { current, port, save, start } = setup();
		expect(await advanceDraftOrder(createDraftOrder(current)!, port)).toEqual({
			accepted: true,
			started: true
		});
		expect(save).not.toHaveBeenCalled();
		expect(start).toHaveBeenCalledTimes(1);
	});

	it('salva il nuovo ordine prima di avviare con lo snapshot aggiornato', async () => {
		const { current, port, save, start } = setup();
		const draft = moveDraftOrder(createDraftOrder(current)!, 11, 0);
		expect(await advanceDraftOrder(draft, port)).toEqual({ accepted: true, started: true });
		expect(save).toHaveBeenCalledWith([11, 12]);
		expect(current.snapshot!.version).toBe(3);
		expect(save.mock.invocationCallOrder[0]).toBeLessThan(start.mock.invocationCallOrder[0]);
	});

	it('non avvia e non ritenta dopo save fallita', async () => {
		const { current, port, save, start } = setup();
		const draft = moveDraftOrder(createDraftOrder(current)!, 11, 0);
		save.mockResolvedValueOnce(false);
		expect(await advanceDraftOrder(draft, port)).toEqual({ accepted: false, started: false });
		expect(save).toHaveBeenCalledTimes(1);
		expect(start).not.toHaveBeenCalled();
	});

	it('non avvia se lo snapshot dopo save non contiene l ordine richiesto', async () => {
		const { current, port, save, start } = setup();
		const draft = moveDraftOrder(createDraftOrder(current)!, 11, 0);
		save.mockResolvedValueOnce(true);
		expect(await advanceDraftOrder(draft, port)).toEqual({ accepted: false, started: false });
		expect(start).not.toHaveBeenCalled();
	});

	it('conserva il salvataggio riuscito senza fingere rollback quando start fallisce', async () => {
		const { current, port, save, start } = setup();
		const draft = moveDraftOrder(createDraftOrder(current)!, 11, 0);
		start.mockResolvedValueOnce(false);
		expect(await advanceDraftOrder(draft, port)).toEqual({ accepted: true, started: false });
		expect(current.snapshot!.order).toEqual([11, 12]);
		expect(save).toHaveBeenCalledTimes(1);
		expect(start).toHaveBeenCalledTimes(1);
	});

	it('non invia alcun comando per una bozza gia obsoleta', async () => {
		const { current, port, save, start } = setup();
		const draft = createDraftOrder(current)!;
		current.snapshot!.version += 1;
		expect(await advanceDraftOrder(draft, port)).toEqual({ accepted: false, started: false });
		expect(save).not.toHaveBeenCalled();
		expect(start).not.toHaveBeenCalled();
	});
});
