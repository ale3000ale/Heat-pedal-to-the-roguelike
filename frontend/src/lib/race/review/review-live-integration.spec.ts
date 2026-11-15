import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ApiError } from '../../api';
import { ReviewCountsStore } from '../../stores/review-counts.svelte';
import type { RaceReview } from '../race-review-types';
import type { ReviewCounts, ReviewInventory } from './review-counts-types';
import type { ConnectionStatus, Listener, StreamEvent } from '../../events/event-types';
const mock = vi.hoisted(() => ({
	read: vi.fn(),
	inventory: vi.fn(),
	draft: vi.fn(),
	save: vi.fn(),
	open: vi.fn(),
	auth: { user: { id: 9 } as { id: number } | null }
}));
vi.mock('../../auth/auth.svelte', () => ({ auth: mock.auth }));
vi.mock('../../api', async (original) => ({
	...(await original<typeof import('../../api')>()),
	api: mock.read
}));
vi.mock('../race-review-api', () => ({
	openReview: mock.open,
	reopenReview: mock.open,
	abandonReview: vi.fn()
}));
vi.mock('./review-counts-api', async (original) => ({
	...(await original<typeof import('./review-counts-api')>()),
	fetchReviewInventory: mock.inventory,
	fetchReviewDraft: mock.draft,
	saveReviewDraft: mock.save,
	confirmReviewCounts: vi.fn()
}));
class FakeClient {
	events = new Set<Listener<StreamEvent>>();
	statuses = new Set<Listener<ConnectionStatus>>();
	subscribe(listener: Listener<StreamEvent>) {
		this.events.add(listener);
		return () => {
			this.events.delete(listener);
		};
	}
	subscribeStatus(listener: Listener<ConnectionStatus>) {
		this.statuses.add(listener);
		void listener('open');
		return () => {
			this.statuses.delete(listener);
		};
	}
	status(value: ConnectionStatus) {
		for (const listener of this.statuses) void listener(value);
	}
	emit() {
		for (const listener of this.events)
			void listener({
				type: 'cards.changed',
				id: '1',
				championshipId: 3,
				pilotId: 1,
				payload: { race_id: 7 }
			});
	}
}
let review: RaceReview;
let inventory: ReviewInventory;
let draft: ReviewCounts | null;
let store: ReviewCountsStore;
let client: FakeClient;
beforeEach(async () => {
	vi.clearAllMocks();
	mock.auth.user = { id: 9 };
	review = {
		race_id: 7,
		in_review: true,
		reviewer_user_id: 9,
		review_started_at: '2099-01-01T00:00:00Z',
		review_expires_at: '2099-01-01T00:15:00Z',
		review_closed_at: null
	};
	inventory = {
		race_id: 7,
		pilots: [
			{
				pilot_id: 1,
				pilot_name: 'Pilota',
				cards: [
					{
						card_name: 'Freno',
						card_path: 'cards/freno.webp',
						total: 3,
						remaining: 1,
						gifted: 1,
						start: 2,
						pool_now: 2,
						pool_max: 7
					}
				]
			}
		]
	};
	draft = null;
	mock.read.mockImplementation(async () => ({ ...review }));
	mock.inventory.mockImplementation(async () => structuredClone(inventory));
	mock.draft.mockImplementation(async () => structuredClone(draft));
	mock.save.mockImplementation(async (_c, _r, data: ReviewCounts) => {
		draft = structuredClone(data);
	});
	const memory = new Map<string, string>();
	vi.stubGlobal('sessionStorage', {
		getItem: (key: string) => memory.get(key) ?? null,
		setItem: (key: string, value: string) => {
			memory.set(key, value);
		}
	});
	client = new FakeClient();
	store = new ReviewCountsStore(3, 7);
	store.connect(1000, client);
	await store.refreshStatus();
});
afterEach(() => {
	store.dispose();
	vi.useRealTimers();
	vi.unstubAllGlobals();
});
describe('collegamento live inventari', () => {
	it('riprende senza POST e fonde eventi preservando conteggi e revocando spunte', async () => {
		expect(mock.open).not.toHaveBeenCalled();
		store.adjust(1, 'Freno', 1);
		store.checked = [1];
		inventory.pilots[0].cards[0].total = 4;
		client.emit();
		await vi.waitFor(() => expect(store.pilots[0].cards[0].total).toBe(4));
		expect(store.pilots[0].cards[0].remaining).toBe(2);
		expect(store.checked).toEqual([]);
		expect(mock.save).not.toHaveBeenCalled();
	});
	it('congela incompatibilita e recupera solo con conferma e copia precedente', async () => {
		store.adjust(1, 'Freno', 1);
		store.adjust(1, 'Freno', 1);
		inventory.pilots[0].cards[0].total = 1;
		await store.refreshStatus();
		expect(store.blocked).toBe(true);
		expect(store.pilots[0].cards[0].remaining).toBe(3);
		expect(await store.confirm()).toBe(false);
		expect(await store.reloadInventory()).toBe(false);
		expect(await store.reloadInventory(true)).toBe(true);
		expect(store.previousPilots[0].cards[0].remaining).toBe(3);
		expect(store.pilots[0].cards[0].remaining).toBe(1);
		expect(store.active).toBe(true);
		expect(mock.save).not.toHaveBeenCalled();
	});
	it('non legge bozze altrui e non trasferisce lavoro a un nuovo inizio', async () => {
		store.adjust(1, 'Freno', 1);
		review.reviewer_user_id = 10;
		mock.draft.mockClear();
		await store.refreshStatus();
		expect(mock.draft).not.toHaveBeenCalled();
		expect(store.active).toBe(false);
		review.reviewer_user_id = 9;
		review.review_started_at = '2099-01-01T00:01:00Z';
		await store.refreshStatus();
		expect(store.blocked).toBe(true);
		expect(store.pilots[0].cards[0].remaining).toBe(2);
		expect(mock.save).not.toHaveBeenCalled();
	});
	it('bozza server invalida non diventa vuota; recupero ignora solo quella bozza confermata', async () => {
		draft = { pilots: [{ pilot_id: 1, cards: [{ card_name: 'Freno', remaining: 9 }] }] };
		await store.refreshStatus();
		expect(store.blocked).toBe(true);
		expect(store.serverDraftText).toContain('9');
		expect(await store.reloadInventory(true)).toBe(true);
		expect(store.active).toBe(true);
		draft.pilots[0].cards[0].remaining = 8;
		await store.refreshStatus();
		expect(store.blocked).toBe(true);
		expect(mock.save).not.toHaveBeenCalled();
	});
	it('errori preservano conteggi e 401 chiude sottoscrizioni e contesto', async () => {
		mock.draft.mockRejectedValueOnce(new ApiError(503, 'Non disponibile'));
		await store.refreshStatus();
		expect(store.synchronized).toBe(false);
		expect(store.pilots).toHaveLength(1);
		mock.read.mockRejectedValueOnce(new ApiError(401, 'Sessione scaduta'));
		await store.refreshStatus();
		expect(mock.auth.user).toBeNull();
		expect(client.events.size).toBe(0);
		expect(client.statuses.size).toBe(0);
	});
	it('non sovrascrive conteggi dopo dispose durante una lettura', async () => {
		let entered!: () => void;
		let release!: (value: ReviewInventory) => void;
		const arrived = new Promise<void>((resolve) => {
			entered = resolve;
		});
		const held = new Promise<ReviewInventory>((resolve) => {
			release = resolve;
		});
		mock.inventory.mockImplementationOnce(() => {
			entered();
			return held;
		});
		const pending = store.refreshStatus();
		await arrived;
		const before = JSON.stringify(store.pilots);
		store.dispose();
		release({ race_id: 7, pilots: [] });
		await pending;
		expect(JSON.stringify(store.pilots)).toBe(before);
		expect(client.events.size).toBe(0);
	});
	it('fallback solo senza open, nessun polling di sicurezza', async () => {
		vi.useFakeTimers();
		const before = mock.read.mock.calls.length;
		await vi.advanceTimersByTimeAsync(5000);
		expect(mock.read).toHaveBeenCalledTimes(before);
		client.status('retrying');
		await vi.advanceTimersByTimeAsync(1000);
		expect(mock.read.mock.calls.length).toBeGreaterThan(before);
		client.status('open');
		const after = mock.read.mock.calls.length;
		await vi.advanceTimersByTimeAsync(5000);
		expect(mock.read).toHaveBeenCalledTimes(after);
	});
});
