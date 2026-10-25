import { describe, expect, it } from 'vitest';
import { draftDeckView } from './draft-deck-view';
import type { DraftPilotDeckRead } from './draft-types';
import type { DraftSessionState } from './draft-session';

function state(): DraftSessionState {
	return {
		status: 'idle', block: null, error: null, completion: null, raceId: null,
		snapshot: {
			id: 1, championship_id: 7, version: 2, phase: 'decks', first_race: true,
			can_manage: false, my_pilot_ids: [11, 12],
			participants: [
				{ pilot_id: 11, name: 'Anna', present: true },
				{ pilot_id: 12, name: 'Luca', present: true },
				{ pilot_id: 13, name: 'Altro', present: true }
			],
			order: [], cards: [], picks: [], preview_slot_id: null, ready: [], current_pilot_id: null
		}
	};
}

function deck(copies = 14): DraftPilotDeckRead {
	return {
		pilot_id: 11, preparation_version: 2, ready: false, inventory_version: 1, game_version: 1,
		inventory: [{ name: 'Carta', path: 'cards/a.webp', copies: 2 }],
		game_deck: copies ? [{ name: 'Carta', path: 'cards/a.webp', copies }] : []
	};
}

describe('vista mazzi e READY', () => {
	it('conta copie, non nomi, e non sottrae nuovamente dall inventario', () => {
		const value = deck();
		const view = draftDeckView(state(), 11, value);
		expect(view.count).toBe(14);
		expect(view.inventory[0].copies).toBe(2);
		view.inventory[0].copies = 1;
		expect(value.inventory[0].copies).toBe(2);
	});

	it('prima gara consente meno di 15, ma non oltre il massimo', () => {
		expect(draftDeckView(state(), 11, deck(0)).canReady).toBe(true);
		expect(draftDeckView(state(), 11, deck(14)).canReady).toBe(true);
		expect(draftDeckView(state(), 11, deck(16)).canReady).toBe(false);
		expect(draftDeckView(state(), 11, deck(15)).canAdd).toBe(false);
	});

	it('dalle gare successive richiede esattamente 15 copie', () => {
		const value = state();
		value.snapshot!.first_race = false;
		expect(draftDeckView(value, 11, deck(14)).canReady).toBe(false);
		expect(draftDeckView(value, 11, deck(15)).canReady).toBe(true);
	});

	it('READY di account soltanto con tutti i propri presenti, mai per insieme vuoto', () => {
		const value = state();
		value.snapshot!.ready = [11];
		expect(draftDeckView(value, 11, null).allOwnReady).toBe(false);
		expect(draftDeckView(value, 11, null).canUnready).toBe(true);
		value.snapshot!.ready = [11, 12];
		expect(draftDeckView(value, 11, null).allOwnReady).toBe(true);
		value.snapshot!.my_pilot_ids = [];
		expect(draftDeckView(value, null, null).allOwnReady).toBe(false);
		expect(draftDeckView(value, null, null).selected).toBeNull();
	});

	it('versioni o READY incoerenti non abilitano modifiche e pronto', () => {
		const value = deck();
		value.preparation_version = 1;
		expect(draftDeckView(state(), 11, value).canEdit).toBe(false);
		value.preparation_version = 2;
		value.ready = true;
		expect(draftDeckView(state(), 11, value).canReady).toBe(false);
	});

	it('non espone altri proprietari e non usa un mazzo mancante come vuoto valido', () => {
		const value = state();
		value.snapshot!.can_manage = true;
		const view = draftDeckView(value, 13, null);
		expect(view.ownPilots.map((pilot) => pilot.pilot_id)).toEqual([11, 12]);
		expect(view.hasDeck).toBe(false);
		expect(view.count).toBeNull();
		expect(view.canReady).toBe(false);
	});
});
