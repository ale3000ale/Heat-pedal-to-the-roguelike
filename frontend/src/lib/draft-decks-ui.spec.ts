import { describe, expect, it, vi } from 'vitest';
import { render } from 'svelte/server';
import DraftDecks from './components/draft-decks.svelte';
import DraftReady from './components/draft-ready.svelte';
import { createDraftDeckSession } from './draft-deck-session';
import type { DraftRead } from './draft-types';
import { DraftStore } from './stores/draft.svelte';

async function setup(ready: number[] = []) {
	const root: DraftRead = {
		id: 1,
		championship_id: 7,
		version: 2,
		phase: 'decks',
		first_race: false,
		can_manage: false,
		my_pilot_ids: [11, 12],
		participants: [
			{ pilot_id: 11, name: 'Anna', present: true },
			{ pilot_id: 12, name: 'Luca', present: true },
			{ pilot_id: 13, name: 'Altro proprietario', present: true }
		],
		order: [],
		cards: [],
		picks: [],
		preview_slot_id: null,
		ready,
		current_pilot_id: null
	};
	const store = new DraftStore({
		draftId: 1,
		getContext: () => 'auth-1:player:1',
		read: async () => root
	});
	await store.refresh();
	const read = vi.fn().mockImplementation(async (_id: number, pilotId: number) => ({
		pilot_id: pilotId,
		preparation_version: 2,
		ready: ready.includes(pilotId),
		inventory_version: 1,
		game_version: 1,
		inventory: [{ name: 'Carta', path: 'cards/a.webp', copies: 2 }],
		game_deck: [{ name: 'Carta', path: 'cards/a.webp', copies: 15 }]
	}));
	const decks = createDraftDeckSession({ store, draftId: 1, read });
	await decks.select(11);
	return { store, decks, read };
}

// Test SSR predisposti: nessuna interazione, animazione o richiesta POST verificata qui.
describe('rendering preparazione mazzi', () => {
	it('mostra solo i propri presenti e conta copie nel mazzo', async () => {
		const { store, decks, read } = await setup();
		const { body } = render(DraftDecks, { props: { store, decks } });
		expect(body).toContain('Anna');
		expect(body).toContain('Luca');
		expect(body).not.toContain('Altro proprietario');
		expect(body).toContain('Mazzo 15/15');
		expect(body).toContain('Inventario modifiche');
		expect(read).toHaveBeenCalledTimes(1);
	});

	it('non mostra READY completo con un solo proprio pilota pronto', async () => {
		const { store, decks } = await setup([11]);
		const { body } = render(DraftDecks, { props: { store, decks } });
		expect(body).toContain('non Pronto');
		expect(body).not.toContain('class="ready-mark');
	});

	it('mostra READY completo quando tutti i propri presenti sono pronti', async () => {
		const { store, decks } = await setup([11, 12]);
		const { body } = render(DraftDecks, { props: { store, decks } });
		expect(body).toContain('READY');
		expect(body).toContain('non Pronto');
		expect(body).not.toContain('Inventario modifiche');
		expect(body).not.toContain('aria-label="I tuoi piloti presenti"');
	});

	it('la schermata READY ha un solo pulsante e rispetta busy', () => {
		const { body } = render(DraftReady, {
			props: { pilotName: 'Anna', busy: true, onnotready: vi.fn() }
		});
		expect(body.match(/<button\b/g)).toHaveLength(1);
		expect(body).toMatch(/<button[^>]*disabled/);
		expect(body).toContain('Anna');
	});
});
