import { describe, expect, it, vi } from 'vitest';
import { render } from 'svelte/server';
import DraftOrder from './components/draft-order.svelte';
import type { DraftRead } from './draft-types';
import type { DraftSessionOptions } from './draft-session';
import { DraftStore } from './stores/draft.svelte';

function snapshot(): DraftRead {
	return {
		id: 1,
		championship_id: 7,
		version: 2,
		phase: 'order',
		first_race: true,
		can_manage: true,
		my_pilot_ids: [11],
		participants: [
			{ pilot_id: 11, name: 'Anna', present: true },
			{ pilot_id: 12, name: 'Luca', present: true },
			{ pilot_id: 13, name: 'Assente', present: false }
		],
		order: [12, 11],
		cards: [],
		picks: [],
		preview_slot_id: null,
		ready: [],
		current_pilot_id: null
	};
}

async function setup(value = snapshot()) {
	const read = vi.fn<NonNullable<DraftSessionOptions['read']>>().mockResolvedValue(value);
	const send = vi.fn<NonNullable<DraftSessionOptions['send']>>();
	const store = new DraftStore({ draftId: 1, getContext: () => 'auth-1:judge:1', read, send });
	await store.refresh();
	return { store, read, send };
}

// Test SSR predisposti: nessun evento pointer, tastiera o clic viene attivato.
describe('rendering ordine draft', () => {
	it('mostra Prima gara e l ordine server senza sorteggi o richieste nel rendering', async () => {
		const { store, read, send } = await setup();
		const { body } = render(DraftOrder, { props: { store } });
		expect(body).toMatch(/<strong[^>]*text-center[^>]*>Prima gara<\/strong>/);
		expect(body.indexOf('Luca')).toBeLessThan(body.indexOf('Anna'));
		expect(body).not.toContain('Assente');
		expect(body).toContain('aria-label="Trascina Luca"');
		expect(body).toContain('aria-label="Sposta su Anna"');
		expect(body).toContain('Avanti');
		expect(read).toHaveBeenCalledTimes(1);
		expect(send).not.toHaveBeenCalled();
	});

	it('non mostra Prima gara nelle gare successive', async () => {
		const value = snapshot();
		value.first_race = false;
		const { store } = await setup(value);
		expect(render(DraftOrder, { props: { store } }).body).not.toContain('Prima gara');
	});

	it('disabilita controlli ai non creatori e non inventa un ordine incoerente', async () => {
		const value = snapshot();
		value.can_manage = false;
		const { store } = await setup(value);
		expect(render(DraftOrder, { props: { store } }).body).toMatch(/<button[^>]*disabled/);
		const broken = snapshot();
		broken.order = [11, 11];
		const other = await setup(broken);
		const body = render(DraftOrder, { props: { store: other.store } }).body;
		expect(body).toContain('Ordine non utilizzabile');
		expect(body).not.toContain('aria-label="Trascina');
	});

	it('non mostra la schermata in una fase diversa', async () => {
		const value = snapshot();
		value.phase = 'decks';
		const { store } = await setup(value);
		expect(render(DraftOrder, { props: { store } }).body).not.toContain('Ordine di scelta');
	});
});
