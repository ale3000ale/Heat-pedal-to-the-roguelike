import { afterEach, describe, expect, it, vi } from 'vitest';
import { createDraftHost } from './draft-host';
import type { DraftHost } from './draft-host-context';
import { openChampionshipDraft, type ChampionshipDraftLaunch } from './championship-draft-launch';
import type { DraftRead } from './draft-types';

const input: ChampionshipDraftLaunch = { championshipId: 7, sessionKey: 'auth-1', canManage: true, closed: false, raceUnfinished: false };
const dto: DraftRead = { id: 1, championship_id: 7, version: 1, phase: 'attendance', first_race: true,
	can_manage: true, my_pilot_ids: [11], participants: [{ pilot_id: 11, name: 'Anna', present: true }],
	order: [], cards: [], picks: [], preview_slot_id: null, ready: [], current_pilot_id: null };
const hosts: DraftHost[] = [];
function host(getKey: () => string | null = () => 'auth-1'): DraftHost {
	const value = createDraftHost({ getContext: () => {
		const key = getKey();
		return key ? { key, userId: 9, role: 'judge' } : null;
	} });
	hosts.push(value);
	return value;
}
function reply(status = 200): Response {
	return new Response(JSON.stringify(status === 200 ? dto : { detail: 'Errore server' }), {
		status, headers: { 'Content-Type': 'application/json' }
	});
}
function deferred<T>() {
	let resolve!: (value: T) => void;
	const promise = new Promise<T>((done) => { resolve = done; });
	return { promise, resolve };
}
afterEach(() => { for (const value of hosts.splice(0)) value.dispose(); vi.unstubAllGlobals(); });

describe('Nuova Gara apre la preparazione', () => {
	it('usa il POST draft e riusa lo store, senza creare una Race o duplicare GET', async () => {
		const fetch = vi.fn().mockResolvedValue(reply());
		vi.stubGlobal('fetch', fetch);
		const registry = host();
		const opened = await openChampionshipDraft(input, registry);
		expect(opened?.state.snapshot?.phase).toBe('attendance');
		expect(await openChampionshipDraft(input, registry)).toBe(opened);
		expect(registry.getState().entries[0].store).toBe(opened);
		expect(fetch).toHaveBeenCalledTimes(1);
		expect(fetch.mock.calls[0][0]).toBe('/api/championships/7/draft');
	});

	it.each([
		{ sessionKey: null }, { canManage: false }, { closed: true },
		{ raceUnfinished: true }, { sessionKey: 'auth-2' }, { championshipId: 0 }
	] satisfies Partial<ChampionshipDraftLaunch>[])('blocca il contesto locale %o senza rete', async (patch) => {
		const fetch = vi.fn();
		vi.stubGlobal('fetch', fetch);
		await expect(openChampionshipDraft({ ...input, ...patch }, host())).rejects.toThrow();
		expect(fetch).not.toHaveBeenCalled();
	});

	it('non invia un secondo POST mentre l apertura e in corso', async () => {
		const pending = deferred<Response>();
		const fetch = vi.fn().mockReturnValueOnce(pending.promise);
		vi.stubGlobal('fetch', fetch);
		const registry = host();
		const first = openChampionshipDraft(input, registry);
		expect(await openChampionshipDraft(input, registry)).toBeNull();
		expect(fetch).toHaveBeenCalledTimes(1);
		pending.resolve(reply());
		expect(await first).not.toBeNull();
	});

	it('non ripiega sul vecchio endpoint e non ritenta dopo errore server', async () => {
		const fetch = vi.fn().mockResolvedValue(reply(500));
		vi.stubGlobal('fetch', fetch);
		const registry = host();
		expect(await openChampionshipDraft(input, registry)).toBeNull();
		await expect(openChampionshipDraft(input, registry)).rejects.toThrow('Rileggi le preparazioni');
		expect(fetch).toHaveBeenCalledTimes(1);
	});

	it('non attribuisce un apertura tardiva alla generazione successiva', async () => {
		let key = 'auth-1';
		const pending = deferred<Response>();
		vi.stubGlobal('fetch', vi.fn().mockReturnValueOnce(pending.promise));
		const registry = host(() => key);
		const opening = openChampionshipDraft(input, registry);
		key = 'auth-2';
		pending.resolve(reply());
		expect(await opening).toBeNull();
		expect(registry.getState().entries).toEqual([]);
	});
});
