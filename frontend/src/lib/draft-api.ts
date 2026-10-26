import { api } from './api';
import type {
	DraftCommandResult,
	DraftCommands,
	DraftPilotDeckRead,
	DraftRead
} from './draft-types';
import {
	draftObject,
	parseDraft,
	parseDraftAction,
	parseDraftDeck,
	requireDraftId
} from './draft-validation';

const fields: Record<keyof DraftCommands, readonly string[]> = {
	attendance: ['version', 'pilot_id', 'present'],
	'attendance/confirm': ['version'],
	order: ['version', 'pilot_ids'],
	start: ['version'],
	preview: ['version', 'slot_id'],
	choice: ['version', 'slot_id'],
	'deck/move': ['version', 'pilot_id', 'path', 'to_game'],
	ready: ['version', 'pilot_id', 'ready'],
	'already-disputed': ['version'],
	cancel: ['version']
};

function validateCommand(action: keyof DraftCommands, command: unknown): void {
	if (!Object.prototype.hasOwnProperty.call(fields, action)) {
		throw new RangeError('Comando draft sconosciuto');
	}
	const row = draftObject(command);
	const expected = fields[action];
	if (Object.keys(row).length !== expected.length || expected.some((key) => !(key in row))) {
		throw new TypeError('Campi comando draft non validi');
	}
	requireDraftId(row.version);
	if ('pilot_id' in row) requireDraftId(row.pilot_id);
	if ('slot_id' in row && !(action === 'preview' && row.slot_id === null)) {
		requireDraftId(row.slot_id);
	}
	for (const key of ['present', 'ready', 'to_game']) {
		if (key in row && typeof row[key] !== 'boolean') throw new TypeError('Booleano non valido');
	}
	if ('pilot_ids' in row) {
		if (!Array.isArray(row.pilot_ids)) throw new TypeError('Ordine non valido');
		row.pilot_ids.forEach(requireDraftId);
		if (new Set(row.pilot_ids).size !== row.pilot_ids.length) {
			throw new TypeError('Piloti duplicati nell ordine');
		}
	}
	if ('path' in row) {
		if (typeof row.path !== 'string' || [...row.path].length < 1 || [...row.path].length > 255) {
			throw new TypeError('Percorso carta non valido');
		}
	}
}

function sameDraft(value: DraftRead, expected: number): DraftRead {
	if (value.id !== expected) throw new TypeError('Risposta riferita a un altra draft');
	return value;
}

/** Legge i modal autorizzati. Propaga ApiError/TypeError; nessun fallback o retry. */
export async function fetchDrafts(doFetch?: typeof fetch): Promise<DraftRead[]> {
	const value = await api<unknown>('/drafts', { fetch: doFetch });
	if (!Array.isArray(value)) throw new TypeError('Elenco draft non valido');
	const result = value.map(parseDraft);
	if (new Set(result.map((draft) => draft.id)).size !== result.length) {
		throw new TypeError('Preparazioni duplicate');
	}
	return result;
}

/** Apre la preparazione del campionato, non una Race; verifica il contesto ricevuto. */
export async function openDraft(
	championshipId: number,
	doFetch?: typeof fetch
): Promise<DraftRead> {
	requireDraftId(championshipId);
	const value = parseDraft(
		await api<unknown>(`/championships/${championshipId}/draft`, { method: 'POST', fetch: doFetch })
	);
	if (value.championship_id !== championshipId) throw new TypeError('Campionato draft discordante');
	return value;
}

/** Recupera una preparazione; RangeError per ID, ApiError per HTTP/rete, TypeError per DTO. */
export async function fetchDraft(draftId: number, doFetch?: typeof fetch): Promise<DraftRead> {
	requireDraftId(draftId);
	return sameDraft(
		parseDraft(await api<unknown>(`/drafts/${draftId}`, { fetch: doFetch })),
		draftId
	);
}

/** Legge il mazzo autorizzato del pilota senza esporre o richiedere inventari sponsor. */
export async function fetchDraftDeck(
	draftId: number,
	pilotId: number,
	doFetch?: typeof fetch
): Promise<DraftPilotDeckRead> {
	requireDraftId(draftId);
	requireDraftId(pilotId);
	const value = parseDraftDeck(
		await api<unknown>(`/drafts/${draftId}/pilots/${pilotId}/deck`, { fetch: doFetch })
	);
	if (value.pilot_id !== pilotId) throw new TypeError('Pilota draft discordante');
	return value;
}

/** Invia esattamente un comando versionato, senza retry o rilettura automatica.
 * action determina payload e ritorno; cancel ritorna void, ready/disputed un esito.
 * RangeError/TypeError prima della rete per input invalidi; ApiError per HTTP/rete.
 * Una risposta inutilizzabile dopo POST non dimostra il rollback della scrittura.
 */
export async function sendDraftCommand<K extends keyof DraftCommands>(
	draftId: number,
	action: K,
	command: DraftCommands[K],
	doFetch?: typeof fetch
): Promise<DraftCommandResult<K>> {
	requireDraftId(draftId);
	validateCommand(action, command);
	const value = await api<unknown>(`/drafts/${draftId}/${action}`, {
		method: 'POST',
		body: command,
		fetch: doFetch
	});
	if (action === 'cancel') return undefined as DraftCommandResult<K>;
	if (action === 'ready' || action === 'already-disputed') {
		const result = parseDraftAction(value);
		if (result.preparation) sameDraft(result.preparation, draftId);
		if (action === 'already-disputed' && result.race_id === null) {
			throw new TypeError('Gara gia disputata senza identificativo gara');
		}
		return result as DraftCommandResult<K>;
	}
	return sameDraft(parseDraft(value), draftId) as DraftCommandResult<K>;
}
