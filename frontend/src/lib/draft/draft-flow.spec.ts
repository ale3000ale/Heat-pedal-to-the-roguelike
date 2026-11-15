import { describe, expect, it, vi } from 'vitest';
import { createDraftFlowContext, draftFlowView } from './draft-flow';
import type { DraftSessionState } from './draft-session';
import type { DraftRead } from './draft-types';
import { DraftStore } from '../stores/draft.svelte';

function snapshot(): DraftRead {
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

function state(): DraftSessionState {
	return {
		status: 'idle',
		snapshot: snapshot(),
		block: null,
		error: null,
		completion: null,
		raceId: null
	};
}

describe('derivazione delle schermate draft', () => {
	it('distingue scelta iniziale locale da presenze e non usa ID di un altra draft', () => {
		expect(draftFlowView(state(), null).screen).toBe('start');
		expect(draftFlowView(state(), 1).screen).toBe('attendance');
		expect(draftFlowView(state(), 2).screen).toBe('start');
	});

	it.each(['order', 'picking', 'decks'] as const)('segue la fase server %s', (phase) => {
		const value = state();
		value.snapshot!.phase = phase;
		expect(draftFlowView(value, 1).screen).toBe(phase);
	});

	it('considera operazioni principali ed esterne senza modificare lo stato', () => {
		const value = state();
		const before = JSON.stringify(value);
		expect(draftFlowView(value, null, true).busy).toBe(true);
		expect(draftFlowView({ ...value, status: 'writing' }, null).busy).toBe(true);
		expect(draftFlowView({ ...value, status: 'loading' }, null).busy).toBe(true);
		expect(JSON.stringify(value)).toBe(before);
	});

	it('tutti pronti non equivalgono a gara creata', () => {
		const value = state();
		value.snapshot!.phase = 'decks';
		value.snapshot!.ready = [11];
		expect(draftFlowView(value, null)).toMatchObject({
			screen: 'decks',
			visible: true,
			raceId: null,
			completion: null
		});
	});

	it('chiude solo secondo conclusione o dismissione e conserva l esito reale', () => {
		const value = state();
		expect(
			draftFlowView(
				{ ...value, status: 'finished', snapshot: null, completion: 'race', raceId: 9 },
				null
			)
		).toMatchObject({ visible: false, screen: 'closed', completion: 'race', raceId: 9 });
		expect(
			draftFlowView({ ...value, status: 'finished', snapshot: null, completion: 'cancelled' }, null)
				.completion
		).toBe('cancelled');
		expect(draftFlowView({ ...value, status: 'disposed', snapshot: null }, null).visible).toBe(
			false
		);
	});

	it('senza snapshot richiede caricamento senza inventare una fase', () => {
		expect(draftFlowView({ ...state(), status: 'empty', snapshot: null }, null).screen).toBe(
			'loading'
		);
	});
});

describe('contesto del coordinatore', () => {
	it('non carica automaticamente e tiene distinta la dismissione dei dettagli da quella principale', async () => {
		const read = vi.fn<() => Promise<DraftRead>>().mockResolvedValue(snapshot());
		const store = new DraftStore({ draftId: 1, getContext: () => 'auth-1:judge:1', read });
		expect(createDraftFlowContext(store)).toBeNull();
		expect(read).not.toHaveBeenCalled();
		await store.refresh();
		const context = createDraftFlowContext(store)!;
		expect(context.owner).toBe(store);
		expect(context.draftId).toBe(1);
		expect(context.decks.getState().status).toBe('empty');
		context.dispose();
		expect(context.decks.getState().status).toBe('disposed');
		expect(store.state.status).toBe('idle');
		expect(read).toHaveBeenCalledTimes(1);
		store.dispose();
		expect(createDraftFlowContext(store)).toBeNull();
	});
});
