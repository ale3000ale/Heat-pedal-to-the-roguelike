import type { CardEntry } from './types';
import type { DraftActionRead, DraftPilotDeckRead, DraftRead } from './draft-types';

/** Legge un oggetto JSON; TypeError per null, array o valori primitivi. */
export function draftObject(value: unknown): Record<string, unknown> {
	if (!value || typeof value !== 'object' || Array.isArray(value)) {
		throw new TypeError('Oggetto draft non valido');
	}
	return value as Record<string, unknown>;
}

/** Verifica ID/versioni senza coercizioni; RangeError prima di richieste non valide. */
export function requireDraftId(value: unknown): asserts value is number {
	if (typeof value !== 'number' || !Number.isSafeInteger(value) || value <= 0) {
		throw new RangeError('ID o versione draft non validi');
	}
}

function id(value: unknown): number {
	try {
		requireDraftId(value);
		return value;
	} catch {
		throw new TypeError('Identificativo nella risposta draft non valido');
	}
}

function nullableId(value: unknown): number | null {
	return value === null ? null : id(value);
}

function flag(value: unknown): boolean {
	if (typeof value !== 'boolean') throw new TypeError('Booleano draft non valido');
	return value;
}

function text(value: unknown, max = Infinity): string {
	if (typeof value !== 'string' || [...value].length < 1 || [...value].length > max) {
		throw new TypeError('Testo draft non valido');
	}
	return value;
}

function array(value: unknown): unknown[] {
	if (!Array.isArray(value)) throw new TypeError('Elenco draft non valido');
	return value;
}

function ids(value: unknown): number[] {
	const result = array(value).map(id);
	if (new Set(result).size !== result.length) throw new TypeError('ID draft duplicati');
	return result;
}

function card(value: unknown): CardEntry {
	const row = draftObject(value);
	const copies = id(row.copies);
	if (copies > 999) throw new TypeError('Numero di copie non valido');
	return { name: text(row.name, 64), path: text(row.path, 255), copies };
}

/** Valida forma e tipi del DTO pubblico e restituisce copie senza campi interni.
 * Non ricostruisce le regole di gioco o i permessi: il server resta autorevole.
 * @throws TypeError per risposte mancanti, malformate o con identificativi duplicati.
 */
export function parseDraft(value: unknown): DraftRead {
	const row = draftObject(value);
	const phase = row.phase;
	if (phase !== 'attendance' && phase !== 'order' && phase !== 'picking' && phase !== 'decks') {
		throw new TypeError('Fase draft non valida');
	}
	const participants = array(row.participants).map((item) => {
		const pilot = draftObject(item);
		return { pilot_id: id(pilot.pilot_id), name: text(pilot.name), present: flag(pilot.present) };
	});
	const cards = array(row.cards).map((item) => {
		const slot = draftObject(item);
		return {
			slot_id: id(slot.slot_id),
			name: text(slot.name, 64),
			path: text(slot.path, 255),
			chosen_by: nullableId(slot.chosen_by)
		};
	});
	if (new Set(participants.map((pilot) => pilot.pilot_id)).size !== participants.length) {
		throw new TypeError('Piloti draft duplicati');
	}
	if (new Set(cards.map((slot) => slot.slot_id)).size !== cards.length) {
		throw new TypeError('Slot draft duplicati');
	}
	return {
		id: id(row.id),
		championship_id: id(row.championship_id),
		version: id(row.version),
		phase,
		first_race: flag(row.first_race),
		can_manage: flag(row.can_manage),
		my_pilot_ids: ids(row.my_pilot_ids),
		participants,
		order: ids(row.order),
		cards,
		picks: ids(row.picks),
		preview_slot_id: nullableId(row.preview_slot_id),
		ready: ids(row.ready),
		current_pilot_id: nullableId(row.current_pilot_id)
	};
}

/** Valida inventario e mazzo del DTO autorizzato; TypeError su dati non utilizzabili. */
export function parseDraftDeck(value: unknown): DraftPilotDeckRead {
	const row = draftObject(value);
	return {
		pilot_id: id(row.pilot_id),
		preparation_version: id(row.preparation_version),
		ready: flag(row.ready),
		inventory_version: id(row.inventory_version),
		game_version: id(row.game_version),
		inventory: array(row.inventory).map(card),
		game_deck: array(row.game_deck).map(card)
	};
}

/** Valida un esito: preparazione aggiornata oppure gara creata, mai entrambi o nessuno. */
export function parseDraftAction(value: unknown): DraftActionRead {
	const row = draftObject(value);
	const preparation = row.preparation === null ? null : parseDraft(row.preparation);
	const race_id = nullableId(row.race_id);
	if ((preparation === null) === (race_id === null)) {
		throw new TypeError('Esito draft ambiguo');
	}
	return { preparation, race_id };
}
