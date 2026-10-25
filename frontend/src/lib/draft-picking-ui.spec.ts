import { describe, expect, it, vi } from 'vitest';
import { render } from 'svelte/server';
import DraftPicking from './components/draft-picking.svelte';
import DraftPickingCard from './components/draft-picking-card.svelte';
import type { DraftCardSlot, DraftRead } from './draft-types';
import type { DraftSessionOptions } from './draft-session';
import { DraftStore } from './stores/draft.svelte';

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
		cards: Array.from({ length: 5 }, (_, index) => ({
			slot_id: index + 1,
			name: 'Carta',
			path: 'cards/a.webp',
			chosen_by: null
		})),
		picks: [],
		preview_slot_id: null,
		ready: [],
		current_pilot_id: 11
	};
}

async function setup(value = snapshot()) {
	const read = vi.fn<NonNullable<DraftSessionOptions['read']>>().mockResolvedValue(value);
	const send = vi.fn<NonNullable<DraftSessionOptions['send']>>();
	const store = new DraftStore({ draftId: 1, getContext: () => 'auth-1:player:1', read, send });
	await store.refresh();
	return { store, send };
}

// Solo SSR: questi casi non attivano zoom, preview, conferme o richieste POST.
describe('rendering scelta carte', () => {
	it('mostra verde e turno proprio, mantenendo distinte copie uguali', async () => {
		const { store, send } = await setup();
		const { body } = render(DraftPicking, { props: { store } });
		expect(body).toContain('bg-emerald-900');
		expect(body).toContain('tocca a te');
		expect(body).toContain('data-slot-id="1"');
		expect(body).toContain('data-slot-id="2"');
		expect(body).toContain('/media/cards/a.webp');
		expect(send).not.toHaveBeenCalled();
	});

	it('mostra rosso e anteprima ricevuta per gli altri utenti', async () => {
		const value = snapshot();
		value.my_pilot_ids = [12];
		value.preview_slot_id = 2;
		const { store, send } = await setup(value);
		const { body } = render(DraftPicking, { props: { store } });
		expect(body).toContain('bg-red-950');
		expect(body).toContain('Tocca a Anna');
		expect(body).toContain('Anteprima di Anna');
		expect(body).toContain('bg-yellow-300/80');
		expect(send).not.toHaveBeenCalled();
	});

	it('mostra Scegli solo sulla copia ingrandita e consentita', () => {
		const slot: DraftCardSlot = {
			slot_id: 1,
			name: 'Carta',
			path: 'cards/a.webp',
			chosen_by: null
		};
		const props = { slot, enlarged: true, chooseAllowed: true, onzoom: vi.fn(), onchoose: vi.fn() };
		expect(render(DraftPickingCard, { props }).body).toContain('Scegli');
		expect(
			render(DraftPickingCard, { props: { ...props, chooseAllowed: false } }).body
		).not.toContain('Scegli');
		expect(render(DraftPickingCard, { props: { ...props, enlarged: false } }).body).not.toContain(
			'Scegli'
		);
	});

	it('riepiloga la scelta col pilota senza riunire copie identiche', async () => {
		const value = snapshot();
		value.cards[0].chosen_by = 11;
		value.picks = [1];
		value.current_pilot_id = 12;
		const { store } = await setup(value);
		const { body } = render(DraftPicking, { props: { store } });
		expect(body).toContain('Carte scelte');
		expect(body).toContain('Scelta da Anna');
		expect(body).toContain('data-slot-id="2"');
	});

	it('non rende la schermata dopo il passaggio ai mazzi', async () => {
		const value = snapshot();
		value.phase = 'decks';
		const { store } = await setup(value);
		expect(render(DraftPicking, { props: { store } }).body).not.toContain('Scelta carte draft');
	});
});
