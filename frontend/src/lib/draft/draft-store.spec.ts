import { describe, expect, it, vi } from 'vitest';
import { ApiError } from '../api';
import type { DraftSessionOptions } from './draft-session';
import type { DraftRead } from './draft-types';
import { DraftStore } from '../stores/draft.svelte';

function snapshot(version = 2): DraftRead {
	return {
		id: 1,
		championship_id: 7,
		version,
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

function deferred<T>() {
	let resolve!: (value: T) => void;
	const promise = new Promise<T>((done) => {
		resolve = done;
	});
	return { promise, resolve };
}

function setup() {
	let context: string | null = 'auth-1:judge:draft-1';
	const read = vi.fn<NonNullable<DraftSessionOptions['read']>>().mockResolvedValue(snapshot());
	const send = vi.fn<NonNullable<DraftSessionOptions['send']>>().mockResolvedValue(snapshot(3));
	const store = new DraftStore({ draftId: 1, getContext: () => context, read, send });
	return {
		store,
		read,
		send,
		changeContext(value: string | null) {
			context = value;
		}
	};
}

describe('adattatore reattivo della sessione draft', () => {
	it('non carica implicitamente e pubblica subito caricamento e risultato', async () => {
		const { store, read } = setup();
		expect(store.state.status).toBe('empty');
		expect(read).not.toHaveBeenCalled();
		const pending = deferred<unknown>();
		read.mockReturnValueOnce(pending.promise);
		const loading = store.refresh();
		expect(store.busy).toBe(true);
		expect(store.state.status).toBe('loading');
		pending.resolve(snapshot());
		expect(await loading).toBe(true);
		expect(store.busy).toBe(false);
		expect(store.state.snapshot).toEqual(snapshot());
	});

	it('non espone lo stato autorevole a mutazioni del consumatore', async () => {
		const { store, send } = setup();
		await store.refresh();
		const view = store.state;
		view.status = 'disposed';
		view.snapshot!.version = 999;
		view.snapshot!.participants[0].name = 'Modificato';
		expect(store.state.status).toBe('idle');
		expect(store.state.snapshot?.participants[0].name).toBe('Anna');
		await store.command('start', {});
		expect(send).toHaveBeenCalledWith(1, 'start', { version: 2 });
	});

	it('pubblica writing senza introdurre una seconda coda o doppi invii', async () => {
		const { store, read, send } = setup();
		await store.refresh();
		const pending = deferred<unknown>();
		send.mockReturnValueOnce(pending.promise);
		const writing = store.command('start', {});
		expect(store.busy).toBe(true);
		expect(store.state.status).toBe('writing');
		expect(await store.command('start', {})).toBe(false);
		expect(await store.refresh()).toBe(false);
		expect(store.busy).toBe(true);
		expect(send).toHaveBeenCalledTimes(1);
		expect(read).toHaveBeenCalledTimes(1);
		pending.resolve(snapshot(3));
		expect(await writing).toBe(true);
		expect(store.busy).toBe(false);
	});

	it('espone conflitto ed errore e li libera solo con refresh esplicito valido', async () => {
		const { store, read, send } = setup();
		await store.refresh();
		send.mockRejectedValueOnce(new ApiError(409, 'Versione cambiata'));
		expect(await store.command('start', {})).toBe(false);
		expect(store.blocked).toBe(true);
		expect(store.state.error).toBe('Versione cambiata');
		expect(store.state.snapshot?.version).toBe(2);
		expect(await store.command('start', {})).toBe(false);
		expect(read).toHaveBeenCalledTimes(1);
		read.mockResolvedValueOnce(snapshot(4));
		expect(await store.refresh()).toBe(true);
		expect(store.blocked).toBe(false);
		expect(store.state.error).toBeNull();
	});

	it('mantiene un esito incerto senza rilettura o reinvio automatici', async () => {
		const { store, read, send } = setup();
		await store.refresh();
		send.mockRejectedValueOnce(new ApiError(0, 'Rete interrotta'));
		await store.command('start', {});
		expect(store.state.block).toBe('uncertain');
		expect(store.busy).toBe(false);
		expect(store.blocked).toBe(true);
		expect(read).toHaveBeenCalledTimes(1);
		expect(send).toHaveBeenCalledTimes(1);
	});

	it('sincronizza il cambio contesto senza rete e scarta il risultato tardivo', async () => {
		const { store, read, changeContext } = setup();
		const pending = deferred<unknown>();
		read.mockReturnValueOnce(pending.promise);
		const loading = store.refresh();
		changeContext('auth-2:player:draft-1');
		store.syncContext();
		expect(store.state.status).toBe('disposed');
		expect(store.state.snapshot).toBeNull();
		expect(store.busy).toBe(false);
		pending.resolve(snapshot());
		expect(await loading).toBe(false);
		expect(store.state.status).toBe('disposed');
		expect(read).toHaveBeenCalledTimes(1);
	});

	it('dispose durante scrittura non viene annullato dal finally della richiesta', async () => {
		const { store, send } = setup();
		await store.refresh();
		const pending = deferred<unknown>();
		send.mockReturnValueOnce(pending.promise);
		const writing = store.command('start', {});
		store.dispose();
		expect(store.state.status).toBe('disposed');
		pending.resolve(snapshot(3));
		expect(await writing).toBe(false);
		expect(store.state.snapshot).toBeNull();
		expect(await store.refresh()).toBe(false);
	});

	it('espone gara creata e annullamento come esiti distinti', async () => {
		const race = setup();
		await race.store.refresh();
		race.send.mockResolvedValueOnce({ preparation: null, race_id: 9 });
		expect(await race.store.command('ready', { pilot_id: 11, ready: true })).toBe(true);
		expect(race.store.state.completion).toBe('race');
		expect(race.store.state.raceId).toBe(9);
		expect(race.store.busy).toBe(false);
		const cancelled = setup();
		await cancelled.store.refresh();
		cancelled.send.mockResolvedValueOnce(undefined);
		expect(await cancelled.store.command('cancel', {})).toBe(true);
		expect(cancelled.store.state.completion).toBe('cancelled');
		expect(cancelled.store.state.raceId).toBeNull();
	});

	it('mantiene isolate istanze diverse senza singleton globale', async () => {
		const first = setup();
		const second = setup();
		await first.store.refresh();
		first.store.dispose();
		expect(first.store.state.status).toBe('disposed');
		expect(second.store.state.status).toBe('empty');
		expect(second.read).not.toHaveBeenCalled();
		expect(await second.store.refresh()).toBe(true);
	});
});
