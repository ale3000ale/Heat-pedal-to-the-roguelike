import { describe, expect, it, vi } from 'vitest';
import {
	canConfirmDraftCancellation,
	draftClosePolicy,
	proposeDraftCancellation
} from './draft-close-policy';
import type { DraftSessionState, DraftSessionStatus } from './draft-session';
import { shouldCloseModal } from './modal-close';

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
			phase: 'decks',
			first_race: true,
			can_manage: true,
			my_pilot_ids: [11, 12],
			participants: [
				{ pilot_id: 11, name: 'Anna', present: true },
				{ pilot_id: 12, name: 'Luca', present: true }
			],
			order: [],
			cards: [],
			picks: [],
			preview_slot_id: null,
			ready: [],
			current_pilot_id: null
		}
	};
}

describe('politica di annullamento draft', () => {
	it('richiede una proposta e non modifica lo snapshot', () => {
		const value = state();
		const before = JSON.stringify(value);
		const proposal = proposeDraftCancellation(value);
		expect(proposal).toEqual({ draftId: 1, version: 2 });
		expect(canConfirmDraftCancellation(value, proposal)).toBe(true);
		expect(canConfirmDraftCancellation(value, null)).toBe(false);
		expect(JSON.stringify(value)).toBe(before);
	});

	it('nasconde la X ai partecipanti non creatori', () => {
		const value = state();
		value.snapshot!.can_manage = false;
		expect(draftClosePolicy(value).showClose).toBe(false);
		expect(proposeDraftCancellation(value)).toBeNull();
	});

	it('blocca READY solo quando tutti i propri presenti sono pronti', () => {
		const value = state();
		value.snapshot!.ready = [11];
		expect(draftClosePolicy(value).canRequest).toBe(true);
		value.snapshot!.ready = [11, 12];
		expect(draftClosePolicy(value)).toMatchObject({ readyLocked: true, showClose: false });
		value.snapshot!.ready = [12];
		expect(draftClosePolicy(value).canRequest).toBe(true);
	});

	it('ignora propri assenti e non applica READY per insieme vuoto', () => {
		const value = state();
		value.snapshot!.participants[1].present = false;
		value.snapshot!.ready = [11];
		expect(draftClosePolicy(value).readyLocked).toBe(true);
		value.snapshot!.my_pilot_ids = [];
		expect(draftClosePolicy(value).readyLocked).toBe(false);
		expect(draftClosePolicy(value).canRequest).toBe(true);
	});

	const unavailable: DraftSessionStatus[] = [
		'empty',
		'loading',
		'writing',
		'blocked',
		'finished',
		'disposed'
	];
	it.each(unavailable)('non propone annullamento durante %s', (status) => {
		const value = { ...state(), status };
		expect(proposeDraftCancellation(value)).toBeNull();
		expect(canConfirmDraftCancellation(value, { draftId: 1, version: 2 })).toBe(false);
	});

	it('rifiuta una proposta dopo cambio versione, draft o disponibilita', () => {
		const value = state();
		const proposal = proposeDraftCancellation(value);
		value.snapshot!.version = 3;
		expect(canConfirmDraftCancellation(value, proposal)).toBe(false);
		value.snapshot!.version = 2;
		value.snapshot!.id = 9;
		expect(canConfirmDraftCancellation(value, proposal)).toBe(false);
		value.snapshot!.id = 1;
		value.snapshot!.ready = [11, 12];
		expect(canConfirmDraftCancellation(value, proposal)).toBe(false);
	});

	it('non permette annullamento senza snapshot', () => {
		const value = { ...state(), snapshot: null };
		expect(draftClosePolicy(value).showClose).toBe(false);
		expect(proposeDraftCancellation(value)).toBeNull();
	});

	it.each(['escape', 'outside'] as const)('non delega %s con closeOnOutside falso', (source) => {
		const request = vi.fn();
		expect(shouldCloseModal(source, false, request)).toBe(false);
		expect(request).not.toHaveBeenCalled();
	});
});
