import { afterEach, describe, expect, it, vi } from 'vitest';
import { ApiError } from './api';
import { createDraftHost, type DraftHostOptions } from './draft-host';
import { startDraftLive } from './draft-live';
import type { EventClient } from './events/event-client';
import type { Listener, StreamEvent } from './events/event-types';
import type { DraftRead } from './draft-types';

function dto(): DraftRead {
	return { id: 1, championship_id: 7, version: 2, phase: 'attendance', first_race: true,
		can_manage: true, my_pilot_ids: [11], participants: [{ pilot_id: 11, name: 'Anna', present: true }],
		order: [], cards: [], picks: [], preview_slot_id: null, ready: [], current_pilot_id: null };
}
function deferred<T>() {
	let resolve!: (value: T) => void;
	const promise = new Promise<T>((done) => { resolve = done; });
	return { promise, resolve };
}
const cleanups: (() => void)[] = [];
function setup(initial?: Promise<unknown>, initiallyBusy = false) {
	let key: string | null = 'auth-1';
	let detailsBusy = initiallyBusy;
	let listener: Listener<StreamEvent> | undefined;
	const stop = vi.fn();
	const list = vi.fn<NonNullable<DraftHostOptions['list']>>().mockResolvedValue([dto()]);
	if (initial) list.mockReturnValueOnce(initial);
	const host = createDraftHost({ getContext: () => key ? { key, userId: 9, role: 'judge' } : null, list });
	const client: Pick<EventClient, 'subscribe'> = { subscribe(run) { listener = run; return stop; } };
	const onError = vi.fn();
	const live = startDraftLive({ host, getContextKey: () => key, isBusy: () => detailsBusy, client, onError });
	cleanups.push(() => { live.dispose(); host.dispose(); });
	return { host, live, list, stop, onError,
		emit(event: StreamEvent) { void listener?.(event); },
		setKey(value: string | null) { key = value; },
		setBusy(value: boolean) { detailsBusy = value; } };
}
const changed: StreamEvent = { type: 'draft.changed', id: '1', championshipId: 7, pilotId: null, payload: { preparation_id: 1 } };
afterEach(() => {
	for (const cleanup of cleanups.splice(0)) cleanup();
	vi.unstubAllGlobals();
});

describe('sincronizzazione registro draft', () => {
	it('legge inizialmente e accorpa i segnali durante una GET', async () => {
		const pending = deferred<unknown>();
		const env = setup(pending.promise);
		for (let i = 0; i < 5; i += 1) env.emit(changed);
		expect(env.list).toHaveBeenCalledTimes(1);
		pending.resolve([dto()]);
		await env.live.wake();
		expect(env.list).toHaveBeenCalledTimes(2);
		expect(env.host.getState().entries).toHaveLength(1);
	});

	it('conserva segnali durante busy del dettaglio e riparte con wake', async () => {
		const env = setup(undefined, true);
		env.emit(changed);
		env.emit(changed);
		expect(env.list).not.toHaveBeenCalled();
		expect(env.live.getState().pending).toBe(true);
		env.setBusy(false);
		await env.live.wake();
		expect(env.list).toHaveBeenCalledTimes(1);
	});

	it('non sovrappone il recupero a un POST e non lo reinvia', async () => {
		const env = setup();
		await env.live.wake();
		const pending = deferred<Response>();
		const fetch = vi.fn().mockReturnValueOnce(pending.promise);
		vi.stubGlobal('fetch', fetch);
		const store = env.host.getState().entries[0].store;
		const command = store.command('attendance', { pilot_id: 11, present: false });
		env.emit(changed);
		await env.live.wake();
		expect(env.list).toHaveBeenCalledTimes(1);
		const updated = { ...dto(), version: 3, participants: [{ pilot_id: 11, name: 'Anna', present: false }] };
		env.list.mockResolvedValue([updated]);
		pending.resolve(new Response(JSON.stringify(updated), { status: 200, headers: { 'Content-Type': 'application/json' } }));
		expect(await command).toBe(true);
		await env.live.wake();
		expect(env.list).toHaveBeenCalledTimes(2);
		expect(fetch).toHaveBeenCalledTimes(1);
		expect(env.host.getState().entries[0].store).toBe(store);
	});

	it('rilegge su resync e ignora eventi di altri domini', async () => {
		const env = setup();
		await env.live.wake();
		env.emit({ type: 'cards.changed', id: '2', championshipId: 7, pilotId: null, payload: {} });
		await env.live.wake();
		expect(env.list).toHaveBeenCalledTimes(1);
		env.emit({ type: 'resync', id: null, reason: 'reconnected' });
		await env.live.wake();
		expect(env.list).toHaveBeenCalledTimes(2);
	});

	it('scarta risposte di una generazione precedente e disiscrive', async () => {
		const pending = deferred<unknown>();
		const env = setup(pending.promise);
		env.setKey('auth-2');
		pending.resolve([dto()]);
		await env.live.wake();
		expect(env.host.getState().entries).toEqual([]);
		expect(env.stop).toHaveBeenCalledTimes(1);
	});

	it('non cicla sugli errori di rete senza nuove invalidazioni', async () => {
		const env = setup(Promise.reject(new ApiError(0, 'Rete')));
		await env.live.wake();
		await env.live.wake();
		expect(env.list).toHaveBeenCalledTimes(1);
		expect(env.host.getState().status).toBe('blocked');
	});

	it('smette di reagire dopo auth.expired', async () => {
		const env = setup();
		await env.live.wake();
		env.emit({ type: 'auth.expired' });
		env.emit(changed);
		await env.live.request();
		expect(env.stop).toHaveBeenCalledTimes(1);
		expect(env.list).toHaveBeenCalledTimes(1);
	});
});
