import { describe, expect, it, vi } from 'vitest';
import { blockDraftEscape, reconcileDraftQueue, selectDraftEntry } from './draft-host-view';
import type { DraftHostEntry } from './draft-host';
import type { DraftRead } from './draft-types';
import { DraftStore } from './stores/draft.svelte';

async function entry(id: number, patch: Partial<DraftRead> = {}): Promise<DraftHostEntry> {
	const dto: DraftRead = {
		id, championship_id: id + 10, version: 2, phase: 'attendance', first_race: true,
		can_manage: true, my_pilot_ids: [11], participants: [{ pilot_id: 11, name: 'Anna', present: true }],
		order: [], cards: [], picks: [], preview_slot_id: null, ready: [], current_pilot_id: null,
		...patch
	};
	const store = new DraftStore({ draftId: id, getContext: () => 'auth-1:judge:9', read: async () => dto, send: async () => undefined });
	await store.refresh();
	return { id, championshipId: dto.championship_id, store };
}

describe('coda locale host draft', () => {
	it('mantiene attivo e coda anche se il server riordina l elenco', async () => {
		const a = await entry(1);
		const b = await entry(2);
		const c = await entry(3);
		const previous = [a.store, b.store];
		const next = reconcileDraftQueue(previous, [c, b, a]);
		expect(next).toEqual([a.store, b.store, c.store]);
		expect(selectDraftEntry(next, [c, b, a])?.store).toBe(a.store);
	});

	it('non ricrea la coda quando cambiano soltanto gli oggetti dell elenco', async () => {
		const a = await entry(1);
		const previous = [a.store];
		expect(reconcileDraftQueue(previous, [{ ...a }])).toBe(previous);
	});

	it('mostra attendance/order al gestore ma non anticipa il modal ai partecipanti', async () => {
		const manager = await entry(1, { phase: 'order' });
		const player = await entry(2, { can_manage: false, phase: 'attendance' });
		expect(reconcileDraftQueue([], [player, manager])).toEqual([manager.store]);
	});

	it('mostra picking/decks solo con propri presenti, senza dedurre la fine da READY', async () => {
		const present = await entry(1, { can_manage: false, phase: 'decks', ready: [11] });
		const absent = await entry(2, { can_manage: false, phase: 'picking', participants: [{ pilot_id: 11, name: 'Anna', present: false }] });
		const other = await entry(3, { can_manage: false, phase: 'picking', my_pilot_ids: [] });
		expect(reconcileDraftQueue([], [absent, other, present])).toEqual([present.store]);
	});

	it('passa al successivo solo dopo conclusione effettiva o rimozione', async () => {
		const a = await entry(1);
		const b = await entry(2);
		await a.store.command('cancel', {});
		expect(reconcileDraftQueue([a.store, b.store], [a, b])).toEqual([b.store]);
		expect(reconcileDraftQueue([b.store], [])).toEqual([]);
	});

	it('non mantiene store dismessi e non duplica le identita', async () => {
		const a = await entry(1);
		const b = await entry(2);
		a.store.dispose();
		expect(reconcileDraftQueue([a.store], [a, b, b])).toEqual([b.store]);
		expect(selectDraftEntry([], [b])).toBeNull();
	});
});

describe('Escape durante il draft', () => {
	it('blocca propagazione e default solo con draft attivo', () => {
		const event = { key: 'Escape', preventDefault: vi.fn(), stopImmediatePropagation: vi.fn() };
		blockDraftEscape(event, false);
		expect(event.preventDefault).not.toHaveBeenCalled();
		blockDraftEscape(event, true);
		expect(event.preventDefault).toHaveBeenCalledTimes(1);
		expect(event.stopImmediatePropagation).toHaveBeenCalledTimes(1);
	});

	it('non blocca gli altri tasti', () => {
		const event = { key: 'Enter', preventDefault: vi.fn(), stopImmediatePropagation: vi.fn() };
		blockDraftEscape(event, true);
		expect(event.preventDefault).not.toHaveBeenCalled();
		expect(event.stopImmediatePropagation).not.toHaveBeenCalled();
	});
});
