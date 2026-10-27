import { describe, expect, it, vi } from 'vitest';
import { render } from 'svelte/server';
import DraftOrder from '../../components/draft/draft-order.svelte';
import type { DraftRead } from '../draft-types';
import type { DraftSessionOptions } from '../draft-session';
import { DraftStore } from '../../stores/draft.svelte';

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
	const accepted = await store.refresh();
	return { store, read, send, accepted };
}
function expectAllButtonsDisabled(body: string): void {
	const buttons = body.match(/<button\b[^>]*>/g) ?? [];
	expect(buttons.length).toBeGreaterThan(0);
	for (const button of buttons)
		expect(button.replace(/"[^"]*"|'[^']*'/g, '""')).toMatch(/\sdisabled(?=\s|=|\/?>)/);
}

// SSR e geometria pura non attestano pointer capture, gesture touch o drop nel browser.
describe('rendering ordine draft', () => {
	it('mostra Prima gara e ordine server senza sorteggi o richieste nel rendering', async () => {
		const { store, read, send } = await setup();
		const { body } = render(DraftOrder, { props: { store } });
		expect(body).toMatch(/<strong[^>]*text-center[^>]*>Prima gara<\/strong>/);
		expect(body.indexOf('Luca')).toBeLessThan(body.indexOf('Anna'));
		expect(body).not.toContain('Assente');
		expect(body).toMatch(/<li\b[^>]*data-order-pilot="12"[^>]*data-order-draggable="true"/);
		expect(body).toContain('aria-label="Sposta su Anna"');
		expect(body).toContain('Avanti');
		expect(read).toHaveBeenCalledTimes(1);
		expect(send).not.toHaveBeenCalled();
	});
	it('offre due frecce accessibili e non un pulsante maniglia', async () => {
		const { store } = await setup();
		const body = render(DraftOrder, { props: { store } }).body;
		expect(body).toContain('↑');
		expect(body).toContain('↓');
		expect(body).toContain('aria-label="Sposta giu Luca"');
		expect(body).not.toContain('aria-label="Trascina');
	});
	it('non mostra Prima gara nelle gare successive', async () => {
		const value = snapshot();
		value.first_race = false;
		const { store } = await setup(value);
		expect(render(DraftOrder, { props: { store } }).body).not.toContain('Prima gara');
	});
	it('disabilita controlli e drag ai non creatori', async () => {
		const value = snapshot();
		value.can_manage = false;
		const { store, accepted, send } = await setup(value);
		expect(accepted).toBe(true);
		const body = render(DraftOrder, { props: { store } }).body;
		expectAllButtonsDisabled(body);
		expect(body).not.toContain('data-order-draggable="true"');
		expect(body).toContain('data-order-draggable="false"');
		expect(send).not.toHaveBeenCalled();
	});
	it('mostra errore e nessuna scheda per ordine unico ma incompleto', async () => {
		const value = snapshot();
		value.order = [11];
		const { store, accepted, send } = await setup(value);
		expect(accepted).toBe(true);
		expect(store.state.status).toBe('idle');
		expect(store.state.snapshot?.phase).toBe('order');
		const body = render(DraftOrder, { props: { store } }).body;
		expect(body).toContain('Ordine non utilizzabile');
		expect(body).not.toContain('data-order-pilot=');
		expectAllButtonsDisabled(body);
		expect(send).not.toHaveBeenCalled();
	});
	it('rifiuta duplicati prima di renderizzare la fase', async () => {
		const value = snapshot();
		value.order = [11, 11];
		const { store, accepted, send } = await setup(value);
		expect(accepted).toBe(false);
		expect(store.state.status).toBe('blocked');
		expect(store.state.block).toBe('read-failed');
		expect(store.state.snapshot).toBeNull();
		expect(store.state.error).toContain('duplicati');
		const body = render(DraftOrder, { props: { store } }).body;
		expect(body).not.toContain('aria-label="Ordine draft"');
		expect(body).not.toContain('data-order-pilot=');
		expect(send).not.toHaveBeenCalled();
	});
	it('non mostra la schermata in fase diversa', async () => {
		const value = snapshot();
		value.phase = 'decks';
		const { store } = await setup(value);
		expect(render(DraftOrder, { props: { store } }).body).not.toContain('Ordine di scelta');
	});
});
