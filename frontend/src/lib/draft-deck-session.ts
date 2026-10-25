import { writable, type Readable } from 'svelte/store';
import { ApiError } from './api';
import { fetchDraftDeck } from './draft-api';
import { draftDeckView } from './draft-deck-view';
import { parseDraftDeck, requireDraftId } from './draft-validation';
import type { DraftPilotDeckRead } from './draft-types';
import type { DraftStore } from './stores/draft.svelte';

export interface DraftDeckState {
	status: 'empty' | 'loading' | 'idle' | 'writing' | 'blocked' | 'disposed';
	pilotId: number | null;
	data: DraftPilotDeckRead | null;
	error: string | null;
	busy: boolean;
}

export interface DraftDeckOptions {
	store: DraftStore;
	draftId: number;
	read?: (draftId: number, pilotId: number) => Promise<unknown>;
}

/** Coordina dettagli autorizzati e comandi dello store, senza rete alla costruzione.
 * Ogni GET e selezione, rilettura esplicita o riconciliazione di una scrittura riuscita.
 * false non prova rollback: il POST puo essere riuscito e la GET successiva fallita.
 * RangeError per draftId invalido. Nessun timer, retry o modifica ottimistica delle carte.
 */
export function createDraftDeckSession(options: DraftDeckOptions) {
	requireDraftId(options.draftId);
	const read = options.read ?? fetchDraftDeck;
	let serial = 0;
	let internal: Omit<DraftDeckState, 'busy'> = {
		status: 'empty', pilotId: null, data: null, error: null
	};

	function copy(): DraftDeckState {
		return {
			...internal,
			data: internal.data ? parseDraftDeck(internal.data) : null,
			busy: internal.status === 'loading' || internal.status === 'writing'
		};
	}
	const channel = writable(copy());
	const subscribe: Readable<DraftDeckState>['subscribe'] = (run, invalidate) =>
		channel.subscribe((value) => run({ ...value, data: value.data ? parseDraftDeck(value.data) : null }), invalidate);

	function update(patch: Partial<typeof internal>): void {
		const next = { ...internal, ...patch };
		if (next.status === internal.status && next.pilotId === internal.pilotId &&
			next.data === internal.data && next.error === internal.error) return;
		internal = next;
		channel.set(copy());
	}

	function dispose(): void {
		serial += 1;
		update({ status: 'disposed', pilotId: null, data: null, error: null });
	}

	/** Sincronizza invalidazioni, senza leggere il server o liberare blocchi da sola. */
	function sync(): void {
		if (internal.status === 'disposed') return;
		const root = options.store.state;
		if (root.status === 'finished' || root.status === 'disposed' ||
			(root.snapshot && root.snapshot.id !== options.draftId)) {
			dispose();
			return;
		}
		const view = draftDeckView(root, internal.pilotId, internal.data);
		if (!view.visible || (internal.pilotId !== null && !view.ownPilots.some((pilot) => pilot.pilot_id === internal.pilotId))) {
			if (internal.pilotId !== null || internal.data !== null || internal.status !== 'empty') {
				serial += 1;
				update({ status: 'empty', pilotId: null, data: null, error: null });
			}
			return;
		}
		if (!copy().busy && internal.data && !view.current) {
			update({ status: 'blocked', error: 'Mazzo non aggiornato alla preparazione: rileggi dal server.' });
		}
	}

	function valid(ticket: number): boolean {
		return ticket === serial && internal.status !== 'disposed';
	}

	async function load(pilotId: number, ticket: number, saved: boolean): Promise<boolean> {
		const root = options.store.state;
		if (!root.snapshot) return false;
		const version = root.snapshot.version;
		update({ status: 'loading', error: null });
		try {
			const data = parseDraftDeck(await read(options.draftId, pilotId));
			options.store.syncContext();
			sync();
			if (!valid(ticket)) return false;
			const current = options.store.state;
			const view = draftDeckView(current, pilotId, data);
			if (!current.snapshot || current.snapshot.id !== options.draftId || current.snapshot.version !== version ||
				data.pilot_id !== pilotId || view.selected?.pilot_id !== pilotId || !view.current) {
				throw new TypeError('Mazzo, versione o contesto non corrispondenti: rileggi la preparazione e il mazzo.');
			}
			update({ status: 'idle', pilotId, data, error: null });
			return true;
		} catch (error) {
			if (!valid(ticket)) return false;
			const denied = error instanceof ApiError && (error.status === 401 || error.status === 403);
			const message = error instanceof Error ? error.message : 'Lettura mazzo non riuscita';
			update({
				status: 'blocked', data: denied ? null : internal.data,
				error: saved ? `Operazione salvata; lettura mazzo non confermata: ${message}` : message
			});
			return false;
		}
	}

	/** Selezione esplicita: un cambio pilota puo superare una GET, non un POST in corso. */
	async function select(pilotId: number): Promise<boolean> {
		options.store.syncContext();
		sync();
		if (internal.status === 'disposed' || internal.status === 'writing' || options.store.busy) return false;
		if (internal.status === 'loading' && internal.pilotId === pilotId) return false;
		const root = options.store.state;
		const view = draftDeckView(root, pilotId, null);
		if (root.status !== 'idle' || !view.visible || !view.ownPilots.some((pilot) => pilot.pilot_id === pilotId)) return false;
		const ticket = ++serial;
		update({ pilotId, data: internal.pilotId === pilotId ? internal.data : null, error: null });
		return load(pilotId, ticket, false);
	}

	async function commit(pilotId: number, operation: () => Promise<boolean>, reload: boolean): Promise<boolean> {
		const ticket = ++serial;
		update({ status: 'writing', pilotId, error: null });
		try {
			const written = await operation();
			sync();
			if (!valid(ticket)) return false;
			if (!written) {
				const root = options.store.state;
				const current = draftDeckView(root, pilotId, internal.data).current;
				update({ status: root.status === 'idle' && current ? 'idle' : 'blocked', error: root.error ?? 'Operazione non confermata.' });
				return false;
			}
			if (reload) return await load(pilotId, ticket, true);
			update({ status: 'empty', data: null, error: null });
			return true;
		} catch (error) {
			if (valid(ticket)) update({ status: 'blocked', error: error instanceof Error ? error.message : 'Esito non verificabile.' });
			return false;
		}
	}

	/** Sposta una copia e riconcilia con una GET; mai sottrarre carte localmente. */
	async function move(path: string, toGame: boolean): Promise<boolean> {
		options.store.syncContext();
		sync();
		if (copy().busy || internal.status === 'disposed' || internal.status === 'blocked') return false;
		const view = draftDeckView(options.store.state, internal.pilotId, internal.data);
		const source = toGame ? view.inventory : view.gameDeck;
		if (!view.canEdit || !view.selected || (toGame && !view.canAdd) || !source.some((card) => card.path === path && card.copies > 0)) return false;
		const pilotId = view.selected.pilot_id;
		return commit(pilotId, () => options.store.command('deck/move', { pilot_id: pilotId, path, to_game: toGame }), true);
	}

	/** READY per proprio presente. La revoca non impone un conteggio o un DTO mazzo disponibile. */
	async function setReady(pilotId: number, ready: boolean): Promise<boolean> {
		options.store.syncContext();
		sync();
		if (copy().busy || internal.status === 'disposed' || internal.status === 'blocked') return false;
		const view = draftDeckView(options.store.state, pilotId, internal.data);
		if (view.selected?.pilot_id !== pilotId || !(ready ? view.canReady : view.canUnready)) return false;
		return commit(pilotId, () => options.store.command('ready', { pilot_id: pilotId, ready }), !ready);
	}

	return {
		owner: options.store, draftId: options.draftId, subscribe, getState: copy,
		select, reload: () => internal.pilotId === null ? Promise.resolve(false) : select(internal.pilotId),
		move, setReady, sync, dispose
	};
}

export type DraftDeckSession = ReturnType<typeof createDraftDeckSession>;
