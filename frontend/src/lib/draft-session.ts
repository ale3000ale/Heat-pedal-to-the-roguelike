import { ApiError } from './api';
import { fetchDraft, sendDraftCommand } from './draft-api';
import type { DraftCommands, DraftRead } from './draft-types';
import { parseDraft, parseDraftAction, requireDraftId } from './draft-validation';

export type DraftSessionStatus = 'empty' | 'loading' | 'idle' | 'writing' | 'blocked' | 'finished' | 'disposed';
export type DraftSessionBlock = 'read-failed' | 'conflict' | 'authorization' | 'uncertain' | null;

export interface DraftSessionState {
	status: DraftSessionStatus;
	snapshot: DraftRead | null;
	block: DraftSessionBlock;
	error: string | null;
	completion: 'race' | 'cancelled' | null;
	raceId: number | null;
}

export interface DraftSessionOptions {
	draftId: number;
	/** Chiave di generazione autenticazione/ruolo/contesto, non il solo user_id. */
	getContext: () => string | null;
	read?: (draftId: number) => Promise<unknown>;
	send?: (
		draftId: number,
		action: keyof DraftCommands,
		command: DraftCommands[keyof DraftCommands]
	) => Promise<unknown>;
}

/** Crea un controller isolato, senza rete iniziale, timer o persistenza locale.
 * getContext deve cambiare anche tra logout e nuovo login dello stesso utente.
 * getState restituisce copie; refresh/command ritornano true solo se applicati.
 * RangeError per draftId invalido, TypeError per contesto iniziale assente.
 * Il chiamante deve dismettere la sessione al cambio contesto e allo smontaggio.
 */
export function createDraftSession(options: DraftSessionOptions) {
	requireDraftId(options.draftId);
	const context = options.getContext();
	if (!context) throw new TypeError('Contesto draft assente');
	const read = options.read ?? fetchDraft;
	const send: NonNullable<DraftSessionOptions['send']> = options.send ?? sendDraftCommand;
	let generation = 0;
	let championshipId: number | null = null;
	let state: DraftSessionState = {
		status: 'empty', snapshot: null, block: null, error: null, completion: null, raceId: null
	};

	/** Scarta lo stato locale e tutti i risultati futuri; non annulla scritture gia inviate. */
	function dispose(): void {
		generation += 1;
		championshipId = null;
		state = {
			status: 'disposed', snapshot: null, block: null, error: null, completion: null, raceId: null
		};
	}

	function live(): boolean {
		if (state.status === 'disposed') return false;
		if (options.getContext() !== context) {
			dispose();
			return false;
		}
		return true;
	}

	function current(ticket: number): boolean {
		return live() && ticket === generation;
	}

	function available(): boolean {
		return live() && state.status !== 'loading' && state.status !== 'writing' && state.status !== 'finished';
	}

	function accept(value: unknown): void {
		const next = parseDraft(value);
		if (next.id !== options.draftId || (championshipId !== null && next.championship_id !== championshipId)) {
			throw new TypeError('Contesto della risposta draft discordante');
		}
		if (state.snapshot && next.version < state.snapshot.version) {
			throw new TypeError('Risposta draft con versione obsoleta');
		}
		championshipId = next.championship_id;
		state = { ...state, status: 'idle', snapshot: next, block: null, error: null };
	}

	function fail(error: unknown, writing: boolean): void {
		const status = error instanceof ApiError ? error.status : null;
		const message = error instanceof Error ? error.message : 'Operazione draft non riuscita';
		if (status === 401 || status === 403) {
			championshipId = null;
			state = { ...state, status: 'blocked', snapshot: null, block: 'authorization', error: message };
		} else if (status === 409) {
			state = { ...state, status: 'blocked', block: 'conflict', error: message };
		} else if (writing && status === 422) {
			state = { ...state, status: 'idle', block: null, error: message };
		} else {
			state = {
				...state, status: 'blocked', block: writing ? 'uncertain' : 'read-failed', error: message
			};
		}
	}

	/** Legge lo stato senza esporre lo snapshot autorevole a mutazioni del consumatore. */
	function getState(): DraftSessionState {
		live();
		return { ...state, snapshot: state.snapshot ? parseDraft(state.snapshot) : null };
	}

	/** Rilettura esplicita; conserva lo snapshot su errore, ma non lo considera aggiornato.
	 * Nessuna richiesta se occupato, terminato o dismesso. Nessun retry o auto-reload.
	 */
	async function refresh(): Promise<boolean> {
		if (!available()) return false;
		const ticket = ++generation;
		state = { ...state, status: 'loading', error: null };
		try {
			const value = await read(options.draftId);
			if (!current(ticket)) return false;
			accept(value);
			return true;
		} catch (error) {
			if (current(ticket)) fail(error, false);
			return false;
		}
	}

	/** Invia un comando solo da snapshot utilizzabile; la versione non viene dal chiamante.
	 * False per richieste bloccate, fallite o risposte tardive. Non ritenta mai.
	 * Errori non classificabili dopo invio bloccano conservativamente come esito incerto.
	 */
	async function command<K extends keyof DraftCommands>(
		action: K,
		payload: Omit<DraftCommands[K], 'version'>
	): Promise<boolean> {
		if (!available() || state.status !== 'idle' || !state.snapshot) return false;
		const body = { ...payload, version: state.snapshot.version } as DraftCommands[keyof DraftCommands];
		const ticket = ++generation;
		state = { ...state, status: 'writing', error: null };
		try {
			const value = await send(options.draftId, action, body);
			if (!current(ticket)) return false;
			if (action === 'cancel') {
				if (value !== undefined) throw new TypeError('Risposta di annullamento inattesa');
				state = { ...state, status: 'finished', snapshot: null, block: null, completion: 'cancelled' };
			} else if (action === 'ready' || action === 'already-disputed') {
				const result = parseDraftAction(value);
				if (result.preparation) {
					if (action === 'already-disputed') throw new TypeError('Gara gia disputata non conclusa');
					accept(result.preparation);
				} else {
					state = {
						...state, status: 'finished', snapshot: null, block: null,
						completion: 'race', raceId: result.race_id
					};
				}
			} else {
				accept(value);
			}
			return true;
		} catch (error) {
			if (current(ticket)) fail(error, true);
			return false;
		}
	}

	return { getState, refresh, command, dispose };
}
