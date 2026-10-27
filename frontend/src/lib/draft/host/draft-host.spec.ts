import { afterEach, describe, expect, it, vi } from 'vitest';
import { ApiError } from '../../api';
import { createDraftHost } from './draft-host';
import type { DraftHostContext, DraftHostOptions } from './draft-host';
import type { DraftRead } from '../draft-types';

function dto(): DraftRead {
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
function deferred<T>() {
	let resolve!: (value: T) => void;
	const promise = new Promise<T>((done) => {
		resolve = done;
	});
	return { promise, resolve };
}
function setup() {
	let context: DraftHostContext | null = { key: '1:9:judge', userId: 9, role: 'judge' };
	const list = vi.fn<NonNullable<DraftHostOptions['list']>>().mockResolvedValue([dto()]);
	const open = vi.fn<NonNullable<DraftHostOptions['open']>>().mockResolvedValue(dto());
	const read = vi.fn<NonNullable<DraftHostOptions['read']>>().mockResolvedValue(dto());
	const host = createDraftHost({ getContext: () => context, list, open, read });
	return {
		host,
		list,
		open,
		read,
		change(value: DraftHostContext | null) {
			context = value;
		}
	};
}
afterEach(() => vi.unstubAllGlobals());

describe('registro draft autorizzato', () => {
	it('non legge alla costruzione e usa i DTO elenco senza GET duplicate', async () => {
		const { host, list, open, read } = setup();
		expect(list).not.toHaveBeenCalled();
		expect(await host.refresh()).toBe(true);
		expect(host.getState().entries[0].store.state.snapshot).toEqual(dto());
		expect(list).toHaveBeenCalledTimes(1);
		expect(read).not.toHaveBeenCalled();
		expect(open).not.toHaveBeenCalled();
	});

	it('apre una volta e riusa lo stesso store, anche dopo recupero', async () => {
		const { host, open } = setup();
		const first = await host.open(7);
		expect(first).not.toBeNull();
		expect(await host.open(7)).toBe(first);
		expect(await host.refresh()).toBe(true);
		expect(host.getState().entries[0].store).toBe(first);
		expect(open).toHaveBeenCalledTimes(1);
	});

	it('non ritenta aperture incerte e richiede prima un recupero', async () => {
		const { host, open } = setup();
		open.mockRejectedValueOnce(new ApiError(0, 'Rete'));
		expect(await host.open(7)).toBeNull();
		expect(await host.open(7)).toBeNull();
		expect(host.getState().recoveryChampionshipIds).toEqual([7]);
		expect(open).toHaveBeenCalledTimes(1);
		expect(await host.refresh()).toBe(true);
		expect(await host.open(7)).toBe(host.getState().entries[0].store);
		expect(open).toHaveBeenCalledTimes(1);
	});

	it('scarta GET tardive di un altro contesto', async () => {
		const { host, list, change } = setup();
		const pending = deferred<unknown>();
		list.mockReturnValueOnce(pending.promise);
		const loading = host.refresh();
		change({ key: '2:10:player', userId: 10, role: 'player' });
		host.sync();
		pending.resolve([dto()]);
		expect(await loading).toBe(false);
		expect(host.getState().entries).toEqual([]);
		expect(host.getState().contextKey).toBe('2:10:player');
	});

	it('scarta POST tardivi dopo logout senza attribuirli al contesto successivo', async () => {
		const { host, open, change } = setup();
		const pending = deferred<unknown>();
		open.mockReturnValueOnce(pending.promise);
		const opening = host.open(7);
		change(null);
		host.sync();
		pending.resolve(dto());
		expect(await opening).toBeNull();
		expect(host.getState().entries).toEqual([]);
		expect(host.getState().recoveryChampionshipIds).toEqual([]);
	});

	it('dismette i dati anche al nuovo accesso dello stesso account', async () => {
		const { host, change } = setup();
		await host.refresh();
		const previous = host.getState().entries[0].store;
		change({ key: '2:9:judge', userId: 9, role: 'judge' });
		host.sync();
		expect(previous.state.status).toBe('disposed');
		expect(host.getState().entries).toEqual([]);
		expect(await host.refresh()).toBe(true);
		expect(host.getState().entries[0].store).not.toBe(previous);
	});

	it('non amplia il ruolo player e non trasforma un elenco corrotto in vuoto', async () => {
		const { host, change, list, open } = setup();
		await host.refresh();
		list.mockResolvedValueOnce([dto(), dto()]);
		expect(await host.refresh()).toBe(false);
		expect(host.getState().entries).toHaveLength(1);
		change({ key: '2:9:player', userId: 9, role: 'player' });
		expect(await host.open(7)).toBeNull();
		expect(open).not.toHaveBeenCalled();
	});

	it('non riconcilia un elenco mentre uno store sta leggendo', async () => {
		const { host, list, read } = setup();
		await host.refresh();
		const pending = deferred<unknown>();
		read.mockReturnValueOnce(pending.promise);
		const loading = host.getState().entries[0].store.refresh();
		expect(await host.refresh()).toBe(false);
		expect(list).toHaveBeenCalledTimes(1);
		pending.resolve(dto());
		await loading;
	});

	it('conserva una conclusione reale una sola volta prima di rimuovere lo store', async () => {
		const { host, list } = setup();
		await host.refresh();
		vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(null, { status: 204 })));
		await host.getState().entries[0].store.command('cancel', {});
		expect(host.takeCompletions()).toEqual([
			{ draftId: 1, championshipId: 7, kind: 'cancelled', raceId: null }
		]);
		list.mockResolvedValueOnce([]);
		expect(await host.refresh()).toBe(true);
		expect(host.getState().entries).toEqual([]);
		expect(host.takeCompletions()).toEqual([]);
	});

	it('rimuove i dati privati su 401 e non riattiva dopo dispose', async () => {
		const { host, list } = setup();
		await host.refresh();
		const store = host.getState().entries[0].store;
		list.mockRejectedValueOnce(new ApiError(401, 'Sessione scaduta'));
		expect(await host.refresh()).toBe(false);
		expect(host.getState().unauthorized).toBe(true);
		expect(store.state.status).toBe('disposed');
		host.dispose();
		expect(await host.refresh()).toBe(false);
		expect(host.getState().status).toBe('disposed');
	});
});
