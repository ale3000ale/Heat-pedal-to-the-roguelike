import { describe, expect, it, vi } from 'vitest';
import { ApiError } from './api';
import { createDraftDeckSession } from './draft-deck-session';
import type { DraftDeckOptions } from './draft-deck-session';
import type { DraftSessionOptions } from './draft-session';
import type { DraftPilotDeckRead, DraftRead } from './draft-types';
import { DraftStore } from './stores/draft.svelte';

function snapshot(): DraftRead {
	return {
		id: 1,
		championship_id: 7,
		version: 2,
		phase: 'decks',
		first_race: true,
		can_manage: false,
		my_pilot_ids: [11, 12],
		participants: [11, 12, 13].map((pilot_id) => ({
			pilot_id,
			name: `Pilota ${pilot_id}`,
			present: true
		})),
		order: [],
		cards: [],
		picks: [],
		preview_slot_id: null,
		ready: [],
		current_pilot_id: null
	};
}

function detail(pilotId: number, version = 2): DraftPilotDeckRead {
	return {
		pilot_id: pilotId,
		preparation_version: version,
		ready: false,
		inventory_version: 1,
		game_version: 1,
		inventory: [{ name: 'Carta', path: 'cards/a.webp', copies: 2 }],
		game_deck: [{ name: 'Carta', path: 'cards/a.webp', copies: 14 }]
	};
}

function deferred<T>() {
	let resolve!: (value: T) => void;
	const promise = new Promise<T>((done) => {
		resolve = done;
	});
	return { promise, resolve };
}

async function setup() {
	let root = snapshot();
	const send = vi
		.fn<NonNullable<DraftSessionOptions['send']>>()
		.mockImplementation(async (_id, action, command) => {
			root = { ...root, version: root.version + 1 };
			if (action === 'ready' && 'pilot_id' in command && 'ready' in command) {
				root.ready = command.ready
					? [...root.ready, command.pilot_id]
					: root.ready.filter((id) => id !== command.pilot_id);
				return { preparation: root, race_id: null };
			}
			return root;
		});
	const store = new DraftStore({
		draftId: 1,
		getContext: () => 'auth-1:player:1',
		read: async () => root,
		send
	});
	await store.refresh();
	const read = vi
		.fn<NonNullable<DraftDeckOptions['read']>>()
		.mockImplementation(async (_id, pilotId) => ({
			...detail(pilotId, store.state.snapshot!.version),
			ready: store.state.snapshot!.ready.includes(pilotId)
		}));
	const decks = createDraftDeckSession({ store, draftId: 1, read });
	return { store, send, read, decks };
}

describe('coordinatore mazzi draft', () => {
	it('non legge alla costruzione e rifiuta piloti altrui', async () => {
		const { decks, read, send } = await setup();
		expect(read).not.toHaveBeenCalled();
		expect(await decks.select(13)).toBe(false);
		expect(read).not.toHaveBeenCalled();
		expect(send).not.toHaveBeenCalled();
	});

	it('scarta una risposta del pilota precedente', async () => {
		const { decks, read } = await setup();
		const pending = deferred<unknown>();
		read.mockReturnValueOnce(pending.promise);
		const first = decks.select(11);
		expect(await decks.select(12)).toBe(true);
		pending.resolve(detail(11));
		expect(await first).toBe(false);
		expect(decks.getState().pilotId).toBe(12);
		expect(decks.getState().data?.pilot_id).toBe(12);
	});

	it('dopo POST riuscito legge i dati reali senza mutazioni ottimistiche', async () => {
		const { decks, read, send } = await setup();
		await decks.select(11);
		const pending = deferred<unknown>();
		read.mockReturnValueOnce(pending.promise);
		const moving = decks.move('cards/a.webp', true);
		await vi.waitFor(() => expect(read).toHaveBeenCalledTimes(2));
		expect(send).toHaveBeenCalledWith(
			1,
			'deck/move',
			expect.objectContaining({ pilot_id: 11, version: 2 })
		);
		expect(decks.getState().data?.game_deck[0].copies).toBe(14);
		pending.resolve({
			...detail(11, 3),
			game_deck: [{ name: 'Carta', path: 'cards/a.webp', copies: 15 }]
		});
		expect(await moving).toBe(true);
		expect(decks.getState().data?.game_deck[0].copies).toBe(15);
	});

	it('non chiama GET dopo POST fallito e non ritenta', async () => {
		const { decks, read, send } = await setup();
		await decks.select(11);
		send.mockRejectedValueOnce(new ApiError(409, 'Conflitto'));
		expect(await decks.move('cards/a.webp', true)).toBe(false);
		expect(read).toHaveBeenCalledTimes(1);
		expect(send).toHaveBeenCalledTimes(1);
	});

	it('distingue POST riuscito da GET fallita e blocca altri movimenti', async () => {
		const { decks, read, send, store } = await setup();
		await decks.select(11);
		read.mockRejectedValueOnce(new ApiError(0, 'Rete'));
		expect(await decks.move('cards/a.webp', true)).toBe(false);
		expect(store.state.snapshot?.version).toBe(3);
		expect(decks.getState().error).toContain('Operazione salvata');
		expect(await decks.move('cards/a.webp', true)).toBe(false);
		expect(send).toHaveBeenCalledTimes(1);
	});

	it('rifiuta dettagli con versione incoerente e non inventa mazzi vuoti', async () => {
		const { decks, read } = await setup();
		read.mockResolvedValueOnce(detail(11, 1));
		expect(await decks.select(11)).toBe(false);
		expect(decks.getState().data).toBeNull();
		expect(decks.getState().status).toBe('blocked');
	});

	it('conferma un pilota e revoca pronto senza richiedere il vecchio conteggio', async () => {
		const { decks, send } = await setup();
		await decks.select(11);
		expect(await decks.setReady(11, true)).toBe(true);
		expect(decks.getState().data).toBeNull();
		expect(await decks.setReady(11, false)).toBe(true);
		expect(send.mock.calls.map((call) => call[1])).toEqual(['ready', 'ready']);
		expect(decks.getState().data?.ready).toBe(false);
	});

	it('dispose elimina i dati e impedisce il ritorno di una GET tardiva', async () => {
		const { decks, read } = await setup();
		const pending = deferred<unknown>();
		read.mockReturnValueOnce(pending.promise);
		const loading = decks.select(11);
		decks.dispose();
		pending.resolve(detail(11));
		expect(await loading).toBe(false);
		expect(decks.getState().data).toBeNull();
		expect(decks.getState().status).toBe('disposed');
	});
});
