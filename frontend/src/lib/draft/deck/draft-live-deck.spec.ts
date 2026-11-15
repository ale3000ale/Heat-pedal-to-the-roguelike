import { describe, expect, it, vi } from 'vitest';
import { createDraftDeckSession } from './draft-deck-session';
import { createDraftLiveDeckRefresh } from './draft-live-deck';
import { DraftStore } from '../../stores/draft.svelte';
import type { DraftRead } from '../draft-types';

async function setup() {
	let version = 2;
	const value = (): DraftRead => ({
		id: 1,
		championship_id: 7,
		version,
		phase: 'decks',
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
	});
	const owner = new DraftStore({
		draftId: 1,
		getContext: () => 'auth-1',
		read: async () => value()
	});
	await owner.refresh();
	const read = vi.fn(async () => ({
		pilot_id: 11,
		preparation_version: version,
		ready: false,
		inventory_version: 1,
		game_version: 1,
		inventory: [],
		game_deck: []
	}));
	const decks = createDraftDeckSession({ store: owner, draftId: 1, read });
	const live = createDraftLiveDeckRefresh();
	return {
		owner,
		decks,
		read,
		live,
		async advance() {
			version += 1;
			await owner.refresh();
		}
	};
}

describe('dettaglio mazzo dopo aggiornamento live', () => {
	it('non duplica il primo caricamento e non rilegge dati gia coerenti', async () => {
		const env = await setup();
		expect(await env.live.refresh(env.owner, env.decks)).toBe(false);
		expect(env.read).not.toHaveBeenCalled();
		await env.decks.select(11);
		expect(await env.live.refresh(env.owner, env.decks)).toBe(false);
		expect(env.read).toHaveBeenCalledTimes(1);
	});

	it('rilegge una volta il dettaglio obsoleto e mantiene il coordinatore', async () => {
		const env = await setup();
		await env.decks.select(11);
		await env.advance();
		expect(await env.live.refresh(env.owner, env.decks)).toBe(true);
		expect(env.decks.getState().data?.preparation_version).toBe(3);
		expect(await env.live.refresh(env.owner, env.decks)).toBe(false);
		expect(env.read).toHaveBeenCalledTimes(2);
	});

	it('non ritenta la stessa versione dopo errore e lascia la rilettura manuale', async () => {
		const env = await setup();
		await env.decks.select(11);
		await env.advance();
		env.read.mockRejectedValueOnce(new Error('Offline'));
		expect(await env.live.refresh(env.owner, env.decks)).toBe(false);
		expect(await env.live.refresh(env.owner, env.decks)).toBe(false);
		expect(env.read).toHaveBeenCalledTimes(2);
		expect(await env.decks.reload()).toBe(true);
	});
});
