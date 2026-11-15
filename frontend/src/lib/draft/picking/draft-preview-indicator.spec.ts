import { describe, expect, it, vi } from 'vitest';
import { render } from 'svelte/server';
import DraftPicking from '../../components/draft/draft-picking.svelte';
import { draftPickingView, proposeDraftPreview } from './draft-picking';
import type { DraftRead } from '../draft-types';
import type { DraftSessionState } from '../draft-session';
import { DraftStore } from '../../stores/draft.svelte';

function snapshot(): DraftRead {
	return {
		id: 1,
		championship_id: 7,
		version: 2,
		phase: 'picking',
		first_race: true,
		can_manage: false,
		my_pilot_ids: [11],
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
		preview_slot_id: 2,
		ready: [],
		current_pilot_id: 11
	};
}

// Solo modello e SSR: nessuna simulazione di clic, zoom o DOM client.
describe('indicatore anteprima draft', () => {
	it.each(['idle', 'writing', 'loading', 'blocked'] as const)(
		'nasconde la propria preview durante %s senza modificare il DTO',
		(status) => {
			const root: DraftSessionState = {
				status,
				snapshot: snapshot(),
				block: null,
				error: null,
				completion: null,
				raceId: null
			};
			const before = JSON.stringify(root);
			expect(draftPickingView(root).previewSlotId).toBeNull();
			expect(draftPickingView(root).ownedTurn).toBe(true);
			expect(proposeDraftPreview(root, 2)).toEqual(status === 'idle' ? { slot_id: 2 } : null);
			expect(JSON.stringify(root)).toBe(before);
		}
	);

	it.each([false, true])('mostra la preview altrui anche con can_manage=%s', async (manager) => {
		const value = snapshot();
		value.my_pilot_ids = [12];
		value.can_manage = manager;
		const read = vi.fn<() => Promise<DraftRead>>().mockResolvedValue(value);
		const store = new DraftStore({ draftId: 1, getContext: () => 'auth-1', read });
		await store.refresh();
		expect(draftPickingView(store.state).previewSlotId).toBe(2);
		const body = render(DraftPicking, { props: { store } }).body;
		expect(body).toContain('Anna sta scegliendo');
		expect(body).toContain('bg-yellow-300/80');
		expect(read).toHaveBeenCalledTimes(1);
	});

	it('non rende nome o alone della propria preview', async () => {
		const read = vi.fn<() => Promise<DraftRead>>().mockResolvedValue(snapshot());
		const store = new DraftStore({ draftId: 1, getContext: () => 'auth-1', read });
		await store.refresh();
		const body = render(DraftPicking, { props: { store } }).body;
		expect(body).toContain('tocca a te');
		expect(body).not.toContain('sta scegliendo');
		expect(body).not.toContain('bg-yellow-300/80');
		expect(store.state.snapshot?.preview_slot_id).toBe(2);
	});
});
