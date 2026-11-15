import { describe, expect, it } from 'vitest';
import {
	canConfirmDraftChoice,
	draftPickingView,
	proposeDraftChoice,
	proposeDraftPreview
} from './draft-picking';
import type { DraftSessionState } from './draft-session';

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
			phase: 'picking',
			first_race: true,
			can_manage: false,
			my_pilot_ids: [11],
			participants: [
				{ pilot_id: 11, name: 'Anna', present: true },
				{ pilot_id: 12, name: 'Luca', present: true }
			],
			order: [11, 12],
			cards: Array.from({ length: 5 }, (_, index) => ({
				slot_id: index + 1,
				name: 'Carta',
				path: 'cards/a.webp',
				chosen_by: null
			})),
			picks: [],
			preview_slot_id: null,
			ready: [],
			current_pilot_id: 11
		}
	};
}

describe('turno e copie draft', () => {
	it('permette al proprietario del pilota, non al semplice gestore', () => {
		const value = state();
		expect(draftPickingView(value).canChoose).toBe(true);
		value.snapshot!.can_manage = true;
		value.snapshot!.my_pilot_ids = [12];
		expect(draftPickingView(value).canChoose).toBe(false);
		expect(proposeDraftPreview(value, 1)).toBeNull();
	});

	it('mantiene distinte copie identiche e non muta lo snapshot', () => {
		const value = state();
		const before = JSON.stringify(value);
		const view = draftPickingView(value);
		expect(view.availableCards.map((slot) => slot.slot_id)).toEqual([1, 2, 3, 4, 5]);
		view.availableCards[0].name = 'Altro';
		expect(JSON.stringify(value)).toBe(before);
		expect(proposeDraftChoice(value, 1)?.slotId).toBe(1);
		expect(proposeDraftChoice(value, 2)?.slotId).toBe(2);
	});

	it('deriva scelte e turno dal server senza rimuovere altre copie', () => {
		const value = state();
		value.snapshot!.cards[0].chosen_by = 11;
		value.snapshot!.picks = [1];
		value.snapshot!.current_pilot_id = 12;
		const view = draftPickingView(value);
		expect(view.availableCards).toHaveLength(4);
		expect(view.pickedCards[0].pilot.name).toBe('Anna');
		expect(view.turn?.name).toBe('Luca');
		expect(view.canChoose).toBe(false);
		value.snapshot!.my_pilot_ids = [11, 12];
		expect(draftPickingView(value).canChoose).toBe(true);
		expect(proposeDraftChoice(value, 1)).toBeNull();
	});

	it('distingue revoca preview da nessun comando autorizzato', () => {
		const value = state();
		expect(proposeDraftPreview(value, 2)).toEqual({ slot_id: 2 });
		expect(proposeDraftPreview(value, null)).toEqual({ slot_id: null });
		expect(proposeDraftPreview(value, 99)).toBeNull();
		value.snapshot!.my_pilot_ids = [];
		expect(proposeDraftPreview(value, null)).toBeNull();
	});

	it('rifiuta conferme obsolete per versione, turno, copia o immagine', () => {
		const value = state();
		const proposal = proposeDraftChoice(value, 1);
		expect(canConfirmDraftChoice(value, proposal)).toBe(true);
		value.snapshot!.version = 3;
		expect(canConfirmDraftChoice(value, proposal)).toBe(false);
		value.snapshot!.version = 2;
		value.snapshot!.cards[0].path = 'cards/changed.webp';
		expect(canConfirmDraftChoice(value, proposal)).toBe(false);
		value.snapshot!.cards[0].path = 'cards/a.webp';
		value.snapshot!.current_pilot_id = 12;
		expect(canConfirmDraftChoice(value, proposal)).toBe(false);
		expect(canConfirmDraftChoice(value, null)).toBe(false);
	});

	it.each(['loading', 'writing', 'blocked'] as const)(
		'non abilita scritture durante %s',
		(status) => {
			const value = { ...state(), status };
			expect(proposeDraftChoice(value, 1)).toBeNull();
			expect(proposeDraftPreview(value, 1)).toBeNull();
		}
	);

	it('non sceglie in decks o con riferimenti incoerenti e non crea una gara', () => {
		const value = state();
		value.snapshot!.phase = 'decks';
		expect(draftPickingView(value).visible).toBe(false);
		expect(proposeDraftChoice(value, 1)).toBeNull();
		value.snapshot!.phase = 'picking';
		value.snapshot!.preview_slot_id = 99;
		expect(draftPickingView(value).coherent).toBe(false);
		expect(value.raceId).toBeNull();
	});
});
