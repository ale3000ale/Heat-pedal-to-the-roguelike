import { describe, expect, it } from 'vitest';
import { ownReviewKey, reconcileReviewInventory } from './review-inventory-reconcile';
import type { ReviewInventoryPilot } from './review-counts-types';
import type { RaceReview } from './race-review-types';

function pilots(): ReviewInventoryPilot[] {
	return [
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
	];
}

function review(): RaceReview {
	return {
		race_id: 7,
		in_review: true,
		reviewer_user_id: 9,
		review_started_at: '2026-10-21T12:00:00',
		review_expires_at: '2026-10-21T12:15:00',
		review_closed_at: null
	};
}

describe('contesto e inventario revisione', () => {
	it('identifica solo la propria revisione e distingue un nuovo inizio', () => {
		const current = review();
		const key = ownReviewKey(current, 9);
		expect(key).not.toBeNull();
		expect(ownReviewKey(current, 8)).toBeNull();
		expect(ownReviewKey({ ...current, in_review: false }, 9)).toBeNull();
		expect(ownReviewKey({ ...current, review_closed_at: 'fine' }, 9)).toBeNull();
		expect(ownReviewKey({ ...current, review_started_at: 'nuovo' }, 9)).not.toBe(key);
	});

	it('adotta conteggi remoti non modificati e aggiorna metadati', () => {
		const base = pilots();
		const remote = pilots();
		remote[0].cards[0].remaining = 0;
		remote[0].cards[0].pool_now = 3;
		const result = reconcileReviewInventory(base, pilots(), remote);
		expect(result.pilots).toEqual(remote);
		expect(result.changedPilotIds).toEqual([1]);
		expect(result.blocked).toBe(false);
	});

	it('conserva conteggi locali validi, nuovi arrivi e immutabilita degli input', () => {
		const base = pilots();
		const local = pilots();
		local[0].cards[0].remaining = 2;
		const remote = pilots();
		remote[0].cards[0].total = 4;
		remote[0].cards.push({ ...remote[0].cards[0], card_name: 'Turbo', remaining: 0 });
		const before = structuredClone([base, local, remote]);
		const result = reconcileReviewInventory(base, local, remote);
		expect(result.pilots[0].cards[0].remaining).toBe(2);
		expect(result.pilots[0].cards[0].total).toBe(4);
		expect(result.pilots[0].cards[1].card_name).toBe('Turbo');
		expect([base, local, remote]).toEqual(before);
		result.pilots[0].cards[0].pool_now = 99;
		expect(remote[0].cards[0].pool_now).toBe(2);
	});

	it('non riduce un conteggio oltre il nuovo totale e conserva tutta la copia locale', () => {
		const base = pilots();
		const local = pilots();
		local[0].cards[0].remaining = 3;
		const remote = pilots();
		remote[0].cards[0].total = 1;
		const result = reconcileReviewInventory(base, local, remote);
		expect(result.blocked).toBe(true);
		expect(result.pilots).toEqual(local);
		expect(result.issues[0]).toMatchObject({ reason: 'out_of_range', remaining: 3, total: 1 });
	});

	it('mantiene modifiche a carte o piloti rimossi come conflitto bloccante', () => {
		const local = pilots();
		local[0].cards[0].remaining = 2;
		const withoutCard = pilots();
		withoutCard[0].cards = [];
		const removedCard = reconcileReviewInventory(pilots(), local, withoutCard);
		const removedPilot = reconcileReviewInventory(pilots(), local, []);
		expect(removedCard.issues[0].reason).toBe('card_removed');
		expect(removedPilot.issues[0].reason).toBe('pilot_removed');
		expect(removedCard.pilots).toEqual(local);
		expect(removedPilot.pilots).toEqual(local);
	});

	it('segnala conteggi concorrenti validi senza sovrascrivere il locale', () => {
		const local = pilots();
		local[0].cards[0].remaining = 2;
		const remote = pilots();
		remote[0].cards[0].remaining = 0;
		const result = reconcileReviewInventory(pilots(), local, remote);
		expect(result.pilots[0].cards[0].remaining).toBe(2);
		expect(result.conflictingPilotIds).toEqual([1]);
		expect(result.changedPilotIds).toEqual([1]);
		expect(result.blocked).toBe(false);
	});

	it('accetta snapshot vuoto riuscito se non cancella modifiche locali', () => {
		const result = reconcileReviewInventory(pilots(), pilots(), []);
		expect(result.pilots).toEqual([]);
		expect(result.blocked).toBe(false);
	});

	it('rifiuta fonti server invalide e carte duplicate senza produrre liste vuote', () => {
		const remote = pilots();
		remote[0].cards[0].remaining = 4;
		expect(() => reconcileReviewInventory(pilots(), pilots(), remote)).toThrow(RangeError);
		const local = pilots();
		local[0].cards.push({ ...local[0].cards[0], card_name: ' FRENO ' });
		expect(() => reconcileReviewInventory(pilots(), local, pilots())).toThrow(RangeError);
	});
});
