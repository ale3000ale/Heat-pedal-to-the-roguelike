import { describe, expect, it, vi } from 'vitest';
import { createRawSnippet } from 'svelte';
import { render } from 'svelte/server';
import { ApiError } from './api';
import DraftFlow from './components/draft-flow.svelte';
import DraftModal from './components/draft-modal.svelte';
import type { DraftPhase, DraftRead } from './draft-types';
import type { DraftSessionOptions } from './draft-session';
import { DraftStore } from './stores/draft.svelte';

function snapshot(phase: DraftPhase): DraftRead {
	return {
		id: 1,
		championship_id: 7,
		version: 2,
		phase,
		first_race: true,
		can_manage: true,
		my_pilot_ids: [11, 12],
		participants: [
			{ pilot_id: 11, name: 'Anna', present: true },
			{ pilot_id: 12, name: 'Luca', present: true }
		],
		order: phase === 'order' || phase === 'picking' ? [11, 12] : [],
		cards:
			phase === 'picking'
				? Array.from({ length: 5 }, (_, index) => ({
						slot_id: index + 1,
						name: 'Carta',
						path: 'cards/a.webp',
						chosen_by: null
					}))
				: [],
		picks: [],
		preview_slot_id: null,
		ready: [],
		current_pilot_id: phase === 'picking' ? 11 : null
	};
}

async function setup(phase: DraftPhase = 'attendance') {
	const read = vi.fn<NonNullable<DraftSessionOptions['read']>>().mockResolvedValue(snapshot(phase));
	const send = vi.fn<NonNullable<DraftSessionOptions['send']>>();
	const store = new DraftStore({ draftId: 1, getContext: () => 'auth-1:judge:1', read, send });
	await store.refresh();
	return { store, read, send };
}

/** Verifica il nome dell'attributo nel tag SSR dopo aver escluso i valori quotati.
 * Le classi disabled:* e gli attributi aria-disabled/data-disabled non lo sostituiscono.
 * Anche disabled="false" e presente come attributo booleano HTML.
 */
function hasDisabledAttribute(tag: string): boolean {
	const attributes = tag.replace(/"[^"]*"|'[^']*'/g, '""');
	return /\sdisabled(?=\s|=|\/?>)/.test(attributes);
}

function closeButtonTag(body: string): string {
	const tag = body
		.match(/<button\b[^>]*>/g)
		?.find((button) => button.includes('aria-label="Chiudi"') && !button.includes('tabindex="-1"'));
	if (!tag) throw new Error('Pulsante X del modal assente nel rendering SSR');
	return tag;
}

const children = createRawSnippet(() => ({ render: () => '<p>Contenuto di prova</p>' }));

describe('attributo disabled nei tag SSR', () => {
	it.each([
		['<button class="disabled:opacity-50 disabled:pointer-events-none">', false],
		["<button class='disabled:opacity-50'>", false],
		['<button aria-disabled="true" data-disabled="true">', false],
		['<button data-label="disabled adesso">', false],
		['<button disabled>', true],
		['<button disabled="">', true],
		['<button disabled="false">', true]
	] as const)('riconosce %s senza leggere le classi', (tag, expected) => {
		expect(hasDisabledAttribute(tag)).toBe(expected);
	});
});

// Casi SSR: non provano clic, effetti client, mantenimento del focus o navigazione.
describe('composizione draft', () => {
	it('mostra il percorso iniziale nel modal senza inviare nuovi comandi', async () => {
		const { store, read, send } = await setup();
		const { body } = render(DraftFlow, { props: { store } });
		expect(body).toContain('Preparazione gara');
		expect(body).toContain('Gara già disputata');
		expect(body).not.toContain('aria-label="Presenze gara"');
		expect(read).toHaveBeenCalledTimes(1);
		expect(send).not.toHaveBeenCalled();
	});

	it.each([
		['order', 'Ordine di scelta'],
		['picking', 'Scelta carte draft'],
		['decks', 'Preparazione mazzi draft']
	] as const)('compone la fase %s', async (phase, marker) => {
		const { store, send } = await setup(phase);
		expect(render(DraftFlow, { props: { store } }).body).toContain(marker);
		expect(send).not.toHaveBeenCalled();
	});

	it('blocca la X con externalBusy mantenendo il default precedente', async () => {
		const { store } = await setup();
		const normal = render(DraftModal, { props: { store, children } }).body;
		const busy = render(DraftModal, { props: { store, children, externalBusy: true } }).body;
		expect(hasDisabledAttribute(closeButtonTag(normal))).toBe(false);
		expect(hasDisabledAttribute(closeButtonTag(busy))).toBe(true);
	});

	it('blocca anche il pulsante di rilettura durante una operazione esterna', async () => {
		const { store, send } = await setup();
		send.mockRejectedValueOnce(new ApiError(409, 'Conflitto'));
		await store.command('start', {});
		const { body } = render(DraftModal, { props: { store, children, externalBusy: true } });
		const reload = body
			.match(/<button\b[^>]*>[\s\S]*?<\/button>/g)
			?.find((button) => button.includes('Rileggi dal server'));
		const tag = reload?.match(/^<button\b[^>]*>/)?.[0] ?? '';
		expect(hasDisabledAttribute(tag)).toBe(true);
	});

	it('non mostra piu il modal dopo la dismissione del controller', async () => {
		const { store } = await setup();
		store.dispose();
		expect(render(DraftFlow, { props: { store } }).body).not.toContain('role="dialog"');
	});
});
