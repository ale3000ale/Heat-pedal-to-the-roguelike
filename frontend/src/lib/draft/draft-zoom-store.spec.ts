import { describe, expect, it, vi } from 'vitest';
import { render } from 'svelte/server';
import { ApiError } from '../api';
import DraftPicking from '../components/draft/draft-picking.svelte';
import { proposeDraftChoice } from './picking/draft-picking';
import type { DraftSessionOptions } from './draft-session';
import type { DraftRead } from './draft-types';
import { DraftStore } from '../stores/draft.svelte';

function deferred<T>() {
	let resolve!: (value: T) => void;
	const promise = new Promise<T>((done) => {
		resolve = done;
	});
	return { promise, resolve };
}

function setup(own = [11]) {
	let context: string | null = 'auth-1';
	const value: DraftRead = {
		id: 1,
		championship_id: 7,
		version: 2,
		phase: 'picking',
		first_race: true,
		can_manage: false,
		my_pilot_ids: own,
		participants: [
			{ pilot_id: 11, name: 'Anna', present: true },
			{ pilot_id: 12, name: 'Luca', present: true }
		],
		order: [11, 12],
		cards: [
			{ slot_id: 1, name: 'Carta', path: 'cards/a.webp', chosen_by: null },
			{ slot_id: 2, name: 'Carta', path: 'cards/a.webp', chosen_by: null }
		],
		picks: [],
		preview_slot_id: null,
		ready: [],
		current_pilot_id: 11
	};
	const read = vi.fn<NonNullable<DraftSessionOptions['read']>>().mockResolvedValue(value);
	const send = vi.fn<NonNullable<DraftSessionOptions['send']>>();
	const store = new DraftStore({ draftId: 1, getContext: () => context, read, send });
	return { value, read, send, store, changeContext: (next: string | null) => (context = next) };
}

// Modello e rendering SSR ripetuto: non prova eventi o rimontaggi DOM client.
describe('zoom per copia nello store draft', () => {
	it('apre, cambia copia e chiude senza rete o mutazioni dei dati', async () => {
		const env = setup();
		expect(env.store.toggleZoom(1)).toBe(false);
		expect(env.read).not.toHaveBeenCalled();
		await env.store.refresh();
		const before = env.store.state;
		expect(env.store.toggleZoom(1)).toBe(true);
		expect(env.store.zoomedSlotId).toBe(1);
		expect(env.store.toggleZoom(2)).toBe(true);
		expect(env.store.zoomedSlotId).toBe(2);
		expect(env.store.toggleZoom(2)).toBe(true);
		expect(env.store.zoomedSlotId).toBeNull();
		expect(env.store.toggleZoom(99)).toBe(false);
		expect(env.store.state).toEqual(before);
		expect(env.read).toHaveBeenCalledTimes(1);
		expect(env.send).not.toHaveBeenCalled();
	});

	it('mantiene lo zoom durante e dopo il POST preview simulato', async () => {
		const env = setup();
		await env.store.refresh();
		env.store.toggleZoom(2);
		const pending = deferred<unknown>();
		env.send.mockReturnValueOnce(pending.promise);
		const writing = env.store.command('preview', { slot_id: 2 });
		expect(env.store.busy).toBe(true);
		expect(env.store.zoomedSlotId).toBe(2);
		expect(env.store.toggleZoom(1)).toBe(false);
		pending.resolve({ ...env.value, version: 3, preview_slot_id: 2 });
		expect(await writing).toBe(true);
		expect(env.store.zoomedSlotId).toBe(2);
		expect(env.send).toHaveBeenCalledWith(1, 'preview', { slot_id: 2, version: 2 });
		expect(env.send).toHaveBeenCalledTimes(1);
	});

	it('preserva lo zoom di chi attende fra nuovi rendering e preview altrui', async () => {
		const env = setup([12]);
		await env.store.refresh();
		env.store.toggleZoom(1);
		const before = render(DraftPicking, { props: { store: env.store } }).body;
		expect(before).toContain(
			'relative col-span-full mx-auto w-44 max-w-full sm:mx-0 sm:w-52 lg:w-60'
		);
		env.value.version = 3;
		env.value.preview_slot_id = 2;
		const pending = deferred<unknown>();
		env.read.mockReturnValueOnce(pending.promise);
		const loading = env.store.refresh();
		expect(env.store.zoomedSlotId).toBe(1);
		pending.resolve(env.value);
		expect(await loading).toBe(true);
		const after = render(DraftPicking, { props: { store: env.store } }).body;
		expect(after).toContain(
			'relative col-span-full mx-auto w-44 max-w-full sm:mx-0 sm:w-52 lg:w-60'
		);
		expect(after).toContain('Anna sta scegliendo');
		expect(after).not.toContain('Scegli');
		expect(env.store.zoomedSlotId).toBe(1);
		expect(proposeDraftChoice(env.store.state, 1)).toBeNull();
		expect(env.send).not.toHaveBeenCalled();
	});

	it('mantiene la copia quando cambiano turno e chosen_by', async () => {
		const env = setup();
		await env.store.refresh();
		env.store.toggleZoom(1);
		env.value.version = 3;
		env.value.cards[0].chosen_by = 11;
		env.value.picks = [1];
		env.value.current_pilot_id = 12;
		await env.store.refresh();
		expect(env.store.zoomedSlotId).toBe(1);
		expect(proposeDraftChoice(env.store.state, 1)).toBeNull();
		const body = render(DraftPicking, { props: { store: env.store } }).body;
		expect(body).toContain('Scelta da Anna');
		// Chi ha gia scelto vede solo le carte: lo zoom resta nello store ma non si rende.
		expect(body).not.toContain('w-44');
		expect(body).not.toContain('<button');
	});

	it('azzera una diversa identita carta e la fine della fase picking', async () => {
		const env = setup();
		await env.store.refresh();
		env.store.toggleZoom(1);
		env.value.version = 3;
		env.value.cards[0].path = 'cards/changed.webp';
		await env.store.refresh();
		expect(env.store.zoomedSlotId).toBeNull();
		env.store.toggleZoom(1);
		env.value.version = 4;
		env.value.phase = 'decks';
		env.value.cards[0].chosen_by = 11;
		env.value.cards[1].chosen_by = 12;
		env.value.picks = [1, 2];
		env.value.current_pilot_id = null;
		await env.store.refresh();
		expect(env.store.zoomedSlotId).toBeNull();
		expect(env.store.toggleZoom(1)).toBe(false);
	});

	it('cambio contesto e risposta tardiva non ripristinano lo zoom', async () => {
		const env = setup();
		await env.store.refresh();
		env.store.toggleZoom(2);
		const pending = deferred<unknown>();
		env.send.mockReturnValueOnce(pending.promise);
		const writing = env.store.command('preview', { slot_id: 2 });
		env.changeContext('auth-2');
		env.store.syncContext();
		expect(env.store.zoomedSlotId).toBeNull();
		pending.resolve({ ...env.value, version: 3, preview_slot_id: 2 });
		expect(await writing).toBe(false);
		expect(env.store.zoomedSlotId).toBeNull();
		const other = setup();
		await other.store.refresh();
		expect(other.store.zoomedSlotId).toBeNull();
		other.store.toggleZoom(1);
		other.store.dispose();
		expect(other.store.zoomedSlotId).toBeNull();
	});

	it.each([401, 403])('azzera lo zoom alla perdita di accesso %s', async (status) => {
		const env = setup();
		await env.store.refresh();
		env.store.toggleZoom(1);
		env.read.mockRejectedValueOnce(new ApiError(status, 'Accesso negato'));
		expect(await env.store.refresh()).toBe(false);
		expect(env.store.state.snapshot).toBeNull();
		expect(env.store.zoomedSlotId).toBeNull();
		expect(env.store.toggleZoom(1)).toBe(false);
		expect(env.read).toHaveBeenCalledTimes(2);
	});
});
