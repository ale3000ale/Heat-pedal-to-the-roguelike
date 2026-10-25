import { describe, expect, it } from 'vitest';
import type { DraftRead } from './draft-types';
import { parseDraft, parseDraftAction, parseDraftDeck } from './draft-validation';

function snapshot(): DraftRead {
	return {
		id: 1,
		championship_id: 7,
		version: 2,
		phase: 'attendance',
		first_race: true,
		can_manage: true,
		my_pilot_ids: [11],
		participants: [{ pilot_id: 11, name: 'Anna', present: true }],
		order: [],
		cards: [],
		picks: [],
		preview_slot_id: null,
		ready: [],
		current_pilot_id: null
	};
}

describe('contratti pubblici draft', () => {
	it('valida tutte le fasi senza riscrivere le regole del server', () => {
		for (const phase of ['attendance', 'order', 'picking', 'decks'] as const) {
			const value = { ...snapshot(), phase };
			expect(parseDraft(value)).toEqual(value);
		}
	});

	it('restituisce copie indipendenti e scarta i campi interni non contrattuali', () => {
		const value = { ...snapshot(), snapshot_json: 'privato' };
		const result = parseDraft(value);
		expect(result).toEqual(snapshot());
		result.participants[0].name = 'Altro';
		result.my_pilot_ids.push(12);
		expect(value.participants[0].name).toBe('Anna');
		expect(value.my_pilot_ids).toEqual([11]);
	});

	it.each([null, [], {}, { ...snapshot(), version: '2' }, { ...snapshot(), first_race: 1 },
		{ ...snapshot(), id: Number.MAX_SAFE_INTEGER + 1 }, { ...snapshot(), phase: 'closed' },
		{ ...snapshot(), my_pilot_ids: [11, 11] }, { ...snapshot(), ready: undefined }])(
		'rifiuta risposte malformate: %j',
		(value) => expect(() => parseDraft(value)).toThrow(TypeError)
	);

	it('mantiene copie identiche distinte tramite slot_id', () => {
		const slot = { slot_id: 1, name: 'Carta', path: 'cards/a.webp', chosen_by: null };
		const value = { ...snapshot(), cards: [slot, { ...slot, slot_id: 2 }] };
		expect(parseDraft(value).cards.map((item) => item.slot_id)).toEqual([1, 2]);
		value.cards[1].slot_id = 1;
		expect(() => parseDraft(value)).toThrow(TypeError);
	});

	it('rifiuta piloti duplicati e campi nullable mancanti', () => {
		const value = snapshot();
		value.participants.push({ ...value.participants[0] });
		expect(() => parseDraft(value)).toThrow(TypeError);
		expect(() => parseDraft({ ...snapshot(), current_pilot_id: undefined })).toThrow(TypeError);
	});

	it('valida carte e versioni senza imporre esattamente 15 copie nel lettore', () => {
		const value = {
			pilot_id: 11, preparation_version: 2, ready: false, inventory_version: 1, game_version: 1,
			inventory: [{ name: 'Carta', path: 'cards/a.webp', copies: 3 }], game_deck: []
		};
		expect(parseDraftDeck(value)).toEqual(value);
		for (const copies of [0, 1.5, 1000, '3']) {
			expect(() => parseDraftDeck({ ...value, inventory: [{ ...value.inventory[0], copies }] })).toThrow(TypeError);
		}
	});

	it('distingue continuazione da conclusione senza inventare una gara', () => {
		expect(parseDraftAction({ preparation: snapshot(), race_id: null }).preparation?.id).toBe(1);
		expect(parseDraftAction({ preparation: null, race_id: 9 }).race_id).toBe(9);
		expect(() => parseDraftAction({ preparation: null, race_id: null })).toThrow(TypeError);
		expect(() => parseDraftAction({ preparation: snapshot(), race_id: 9 })).toThrow(TypeError);
	});
});
