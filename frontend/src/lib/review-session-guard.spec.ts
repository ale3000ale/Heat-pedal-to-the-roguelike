import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { RaceReview } from './race-review-types';
import { ReviewCountsStore } from './stores/review-counts.svelte';

const mock = vi.hoisted(() => ({
	read: vi.fn(),
	open: vi.fn(),
	inventory: vi.fn(),
	draft: vi.fn(),
	save: vi.fn(),
	confirm: vi.fn(),
	abandon: vi.fn(),
	auth: { user: { id: 9 } }
}));
vi.mock('./auth.svelte', () => ({ auth: mock.auth }));
vi.mock('./api', async (original) => ({
	...(await original<typeof import('./api')>()),
	api: mock.read
}));
vi.mock('./race-review-api', () => ({
	openReview: mock.open,
	reopenReview: mock.open,
	abandonReview: mock.abandon
}));
vi.mock('./review-counts-api', async (original) => ({
	...(await original<typeof import('./review-counts-api')>()),
	fetchReviewInventory: mock.inventory,
	fetchReviewDraft: mock.draft,
	saveReviewDraft: mock.save,
	confirmReviewCounts: mock.confirm
}));
let review: RaceReview;
let store: ReviewCountsStore;
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
	mock.read.mockImplementation(async () => ({ ...review }));
	mock.open.mockImplementation(async () => ({ ...review }));
	mock.inventory.mockResolvedValue({
		race_id: 7,
		pilots: [{ pilot_id: 1, pilot_name: 'Pilota', cards: [] }]
	});
	mock.draft.mockResolvedValue(null);
	mock.save.mockResolvedValue(undefined);
	vi.stubGlobal('sessionStorage', { getItem: () => null, setItem: vi.fn() });
	store = new ReviewCountsStore(3, 7);
	await store.start();
});
afterEach(() => {
	store.dispose();
	vi.unstubAllGlobals();
});

describe('guardie scritture conteggi', () => {
	it('consente il salvataggio esplicito nel contesto invariato', async () => {
		expect(store.active).toBe(true);
		expect(await store.navigate(-1, true)).toBe(true);
		expect(mock.save).toHaveBeenCalledOnce();
		expect(store.checked).toEqual([1]);
	});
	it('non invia la bozza se il revisore cambia prima del click', async () => {
		review.reviewer_user_id = 10;
		expect(await store.navigate(-1, true)).toBe(false);
		expect(mock.save).not.toHaveBeenCalled();
		expect(store.pilots).toHaveLength(1);
		expect(store.active).toBe(false);
	});
	it('non conferma in un nuovo inizio dello stesso revisore', async () => {
		store.checked = [1];
		review.review_started_at = '2099-01-01T00:01:00Z';
		expect(await store.confirm()).toBe(false);
		expect(mock.confirm).not.toHaveBeenCalled();
	});
	it('non rinuncia se cambia contesto fra PUT e DELETE', async () => {
		mock.save.mockImplementationOnce(async () => {
			review.reviewer_user_id = 10;
		});
		expect(await store.abandon()).toBe(false);
		expect(mock.save).toHaveBeenCalledOnce();
		expect(mock.abandon).not.toHaveBeenCalled();
	});
	it('blocca il vecchio store quando cambia utente autenticato', async () => {
		mock.auth.user = { id: 10 };
		expect(store.active).toBe(false);
		expect(await store.navigate(-1, true)).toBe(false);
		expect(mock.save).not.toHaveBeenCalled();
	});
	it('non procede a PUT dopo dispose durante la verifica', async () => {
		let release!: (value: RaceReview) => void;
		mock.read.mockReturnValueOnce(
			new Promise<RaceReview>((resolve) => {
				release = resolve;
			})
		);
		const pending = store.navigate(-1, true);
		store.dispose();
		release({ ...review });
		expect(await pending).toBe(false);
		expect(mock.save).not.toHaveBeenCalled();
	});
});
