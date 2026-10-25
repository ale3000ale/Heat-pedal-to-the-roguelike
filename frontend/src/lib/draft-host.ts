import { writable, type Readable } from 'svelte/store';
import { ApiError } from './api';
import { fetchDraft, fetchDrafts, openDraft } from './draft-api';
import { parseDraft, requireDraftId } from './draft-validation';
import type { DraftRead } from './draft-types';
import type { Role } from './types';
import { DraftStore } from './stores/draft.svelte';

export interface DraftHostContext {
	key: string;
	userId: number;
	role: Role;
}
export interface DraftHostEntry {
	id: number;
	championshipId: number;
	store: DraftStore;
}
export interface DraftHostCompletion {
	draftId: number;
	championshipId: number;
	kind: 'race' | 'cancelled';
	raceId: number | null;
}
export interface DraftHostState {
	contextKey: string | null;
	status: 'idle' | 'loading' | 'opening' | 'blocked' | 'disposed';
	busy: boolean;
	entries: DraftHostEntry[];
	recoveryChampionshipIds: number[];
	completions: DraftHostCompletion[];
	unauthorized: boolean;
	error: string | null;
}
export interface DraftHostOptions {
	getContext: () => DraftHostContext | null;
	list?: () => Promise<unknown>;
	open?: (championshipId: number) => Promise<unknown>;
	read?: (draftId: number) => Promise<unknown>;
}

type Managed = DraftHostEntry & { seed: DraftRead | null };

function same(a: DraftHostContext | null, b: DraftHostContext | null): boolean {
	return a === null || b === null ? a === b : a.key === b.key && a.userId === b.userId && a.role === b.role;
}

/** Registro a istanze, senza richieste iniziali, polling o connessioni.
 * Il chiamante sincronizza il contesto e richiede refresh/open espliciti.
 * Conserva gli store per ID, invalida risposte di altre generazioni e non ritenta POST.
 * Le completions provengono solo dagli esiti reali dei controller, non da sparizioni REST.
 */
export function createDraftHost(options: DraftHostOptions) {
	const list = options.list ?? fetchDrafts;
	const openRequest = options.open ?? openDraft;
	const read = options.read ?? fetchDraft;
	let bound: DraftHostContext | null = null;
	let serial = 0;
	let disposed = false;
	let entries = new Map<number, Managed>();
	const recovery = new Set<number>();
	const seen = new Set<number>();
	let completions: DraftHostCompletion[] = [];
	let status: DraftHostState['status'] = 'idle';
	let error: string | null = null;
	let unauthorized = false;

	function context(): DraftHostContext | null {
		const value = options.getContext();
		if (!value || !value.key || !Number.isSafeInteger(value.userId) || value.userId < 1 ||
			!(['admin', 'judge', 'player'] as string[]).includes(value.role)) return null;
		return { key: value.key, userId: value.userId, role: value.role };
	}
	function remember(entry: Managed): boolean {
		const state = entry.store.state;
		if (state.status !== 'finished' || state.completion === null || seen.has(entry.id)) return false;
		seen.add(entry.id);
		completions.push({ draftId: entry.id, championshipId: entry.championshipId, kind: state.completion, raceId: state.raceId });
		return true;
	}
	function snapshot(): DraftHostState {
		return {
			contextKey: bound?.key ?? null, status, busy: status === 'loading' || status === 'opening',
			entries: [...entries.values()].map(({ id, championshipId, store }) => ({ id, championshipId, store })),
			recoveryChampionshipIds: [...recovery], completions: completions.map((item) => ({ ...item })),
			unauthorized, error
		};
	}
	const channel = writable(snapshot());
	const subscribe: Readable<DraftHostState>['subscribe'] = (run, invalidate) => channel.subscribe((value) => run({
		...value, entries: value.entries.map((entry) => ({ ...entry })),
		recoveryChampionshipIds: [...value.recoveryChampionshipIds], completions: value.completions.map((item) => ({ ...item }))
	}), invalidate);
	const publish = () => channel.set(snapshot());

	function clear(): void {
		for (const entry of entries.values()) entry.store.dispose();
		entries.clear();
		recovery.clear();
		seen.clear();
		completions = [];
	}

	/** Senza rete; da collegare a sessionKey, utente e ruolo nel futuro host UI. */
	function sync(): void {
		if (disposed) return;
		const next = context();
		if (!same(next, bound)) {
			serial += 1;
			clear();
			bound = next;
			status = 'idle';
			error = null;
			unauthorized = false;
			publish();
			return;
		}
		let changed = false;
		for (const entry of entries.values()) changed = remember(entry) || changed;
		if (changed) publish();
	}
	function valid(ticket: number, expected: DraftHostContext): boolean {
		sync();
		return !disposed && serial === ticket && same(bound, expected);
	}
	function storesBusy(): boolean {
		return [...entries.values()].some((entry) => entry.store.busy);
	}
	function failure(cause: unknown): void {
		unauthorized = cause instanceof ApiError && (cause.status === 401 || cause.status === 403);
		if (unauthorized) clear();
		status = 'blocked';
		error = cause instanceof Error ? cause.message : 'Registro draft non aggiornato';
		publish();
	}

	function make(dto: DraftRead, expected: DraftHostContext): Managed {
		const holder: { seed: DraftRead | null } = { seed: dto };
		const store = new DraftStore({
			draftId: dto.id,
			getContext: () => !disposed && same(context(), expected) ? expected.key : null,
			read: async (id) => {
				if (holder.seed) {
					const value = holder.seed;
					holder.seed = null;
					return value;
				}
				return read(id);
			}
		});
		return {
			id: dto.id, championshipId: dto.championship_id, store,
			get seed() { return holder.seed; },
			set seed(value: DraftRead | null) { holder.seed = value; }
		};
	}
	async function adopt(entry: Managed, dto: DraftRead): Promise<boolean> {
		if (entry.store.busy) return false;
		entry.seed = dto;
		try { return await entry.store.refresh(); }
		finally { entry.seed = null; }
	}

	/** Una GET elenco; riusa i DTO gia autorizzati per aggiornare gli store senza GET duplicate.
	 * Non sovrascrive scritture in corso o versioni piu recenti. Una rilettura scartata
	 * richiede un nuovo comando esplicito; non e una riconciliazione atomica multi-store.
	 */
	async function refresh(): Promise<boolean> {
		sync();
		if (disposed || !bound || status === 'loading' || status === 'opening' || storesBusy()) return false;
		const expected = { ...bound };
		const ticket = ++serial;
		const created: Managed[] = [];
		status = 'loading'; error = null; publish();
		try {
			const raw = await list();
			if (!valid(ticket, expected)) return false;
			if (!Array.isArray(raw)) throw new TypeError('Elenco draft non valido');
			const values = raw.map(parseDraft);
			if (new Set(values.map((dto) => dto.id)).size !== values.length ||
				new Set(values.map((dto) => dto.championship_id)).size !== values.length) {
				throw new TypeError('Preparazioni duplicate nell elenco');
			}
			if (storesBusy()) throw new Error('Rilettura scartata: operazione draft in corso.');
			for (const dto of values) {
				const old = entries.get(dto.id);
				const state = old?.store.state;
				if (old && old.championshipId !== dto.championship_id) throw new TypeError('Campionato della draft cambiato');
				if (state?.status === 'finished' || (state?.snapshot && state.snapshot.version > dto.version)) {
					throw new Error('Elenco precedente allo stato corrente: recupera nuovamente dal server.');
				}
			}
			const next = new Map<number, Managed>();
			for (const dto of values) {
				let entry = entries.get(dto.id);
				if (!entry || entry.store.state.status === 'disposed') {
					entry = make(dto, expected);
					created.push(entry);
				}
				if (!(await adopt(entry, dto))) throw new Error('Snapshot draft non applicato: verifica il contesto.');
				if (!valid(ticket, expected)) return false;
				next.set(dto.id, entry);
			}
			if (storesBusy()) throw new Error('Rilettura scartata: una preparazione e occupata.');
			for (const entry of entries.values()) {
				if (next.get(entry.id)?.store !== entry.store) {
					remember(entry);
					entry.store.dispose();
				}
			}
			entries = next;
			recovery.clear(); status = 'idle'; unauthorized = false; error = null; publish();
			return true;
		} catch (cause) {
			if (valid(ticket, expected)) failure(cause);
			return false;
		} finally {
			for (const entry of created) if (entries.get(entry.id)?.store !== entry.store) entry.store.dispose();
		}
	}

	/** Apertura esplicita solo per gestori; riusa l'esistente e non ritenta POST incerti.
	 * RangeError per ID invalido. Null indica blocco/errore/risposta tardiva, non rollback.
	 */
	async function open(championshipId: number): Promise<DraftStore | null> {
		requireDraftId(championshipId);
		sync();
		if (disposed || !bound) return null;
		if (bound.role !== 'admin' && bound.role !== 'judge') {
			error = 'Solo admin e giudice possono aprire una preparazione.'; publish(); return null;
		}
		if (status === 'loading' || status === 'opening' || status === 'blocked' || storesBusy() || recovery.has(championshipId)) return null;
		const existing = [...entries.values()].find((entry) => entry.championshipId === championshipId &&
			entry.store.state.status !== 'finished' && entry.store.state.status !== 'disposed');
		if (existing) return existing.store;
		const expected = { ...bound };
		const ticket = ++serial;
		let created: Managed | null = null;
		status = 'opening'; error = null; publish();
		try {
			const raw = await openRequest(championshipId);
			if (!valid(ticket, expected)) return null;
			const dto = parseDraft(raw);
			if (dto.championship_id !== championshipId || entries.has(dto.id)) throw new TypeError('Risposta apertura draft discordante');
			created = make(dto, expected);
			if (!(await adopt(created, dto))) throw new Error('Preparazione ricevuta ma non utilizzabile: recupera dal server.');
			if (!valid(ticket, expected)) return null;
			entries.set(dto.id, created);
			status = 'idle'; unauthorized = false; error = null; publish();
			return created.store;
		} catch (cause) {
			if (valid(ticket, expected)) {
				if (!(cause instanceof ApiError) || cause.status === 0 || cause.status >= 500 || cause.status === 409) recovery.add(championshipId);
				failure(cause);
			}
			return null;
		} finally {
			if (created && entries.get(created.id)?.store !== created.store) created.store.dispose();
		}
	}

	/** Consuma solo esiti reali del contesto corrente, prima di eventuali navigazioni. */
	function takeCompletions(): DraftHostCompletion[] {
		sync();
		const values = completions.map((item) => ({ ...item }));
		completions = [];
		publish();
		return values;
	}
	function dispose(): void {
		if (disposed) return;
		disposed = true; serial += 1; clear(); bound = null;
		status = 'disposed'; error = null; unauthorized = false; publish();
	}
	return { subscribe, sync, refresh, open, takeCompletions, dispose, getState: () => { sync(); return snapshot(); } };
}
