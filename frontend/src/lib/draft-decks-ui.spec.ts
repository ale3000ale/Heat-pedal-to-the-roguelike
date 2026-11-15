import { describe, expect, it, vi } from 'vitest';
import { render } from 'svelte/server';
import DraftDecks from './components/draft-decks.svelte';
import DraftReady from './components/draft-ready.svelte';
import { createDraftDeckSession } from './draft-deck-session';
import type { DraftRead } from './draft-types';
import { DraftStore } from './stores/draft.svelte';

function deferred<T>() {
	let resolve!: (value: T) => void;
	const promise = new Promise<T>((done) => {
		resolve = done;
	});
	return { promise, resolve };
}

/** Estrae gli attributi SSR del messaggio, non misura il suo layout nel browser. */
function feedbackTag(body: string, kind: 'busy' | 'verification'): string {
	const tag = body.match(/<p\b[^>]*>/g)?.find((item) => item.includes(`data-draft-deck-${kind}`));
	if (!tag) throw new Error('Riga di feedback assente');
	return tag;
}

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
	return { store, decks, read, root };
}

// SSR e trasporti simulati: nessuna geometria, animazione o interazione DOM client.
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

	it('mantiene le righe del feedback durante la rilettura senza cambiare carte', async () => {
		const { store, decks, read } = await setup();
		const initial = decks.getState().data;
		const before = render(DraftDecks, { props: { store, decks } }).body;
		expect(feedbackTag(before, 'busy')).toContain('invisible');
		expect(feedbackTag(before, 'busy')).toContain('aria-hidden="true"');
		const pending = deferred<unknown>();
		read.mockReturnValueOnce(pending.promise);
		const loading = decks.reload();
		expect(decks.getState().busy).toBe(true);
		const during = render(DraftDecks, { props: { store, decks } }).body;
		expect(feedbackTag(during, 'busy')).not.toContain('invisible');
		expect(feedbackTag(during, 'busy')).toContain('aria-hidden="false"');
		expect(decks.getState().data).toEqual(initial);
		pending.resolve(initial);
		expect(await loading).toBe(true);
		const after = render(DraftDecks, { props: { store, decks } }).body;
		for (const body of [before, during, after]) {
			expect(body).toContain('data-draft-deck-feedback');
			expect(feedbackTag(body, 'verification')).toContain('invisible');
			expect(body).toContain('Inventario modifiche');
			expect(body).toContain('Mazzo 15/15');
		}
		expect(feedbackTag(after, 'busy')).toContain('invisible');
		expect(decks.getState().data).toEqual(initial);
		expect(read).toHaveBeenCalledTimes(2);
	});

	it('riserva anche la verifica quando i dettagli diventano obsoleti', async () => {
		const { store, decks, read, root } = await setup();
		const before = render(DraftDecks, { props: { store, decks } }).body;
		expect(feedbackTag(before, 'verification')).toContain('invisible');
		root.version = 3;
		await store.refresh();
		decks.sync();
		const stale = render(DraftDecks, { props: { store, decks } }).body;
		expect(feedbackTag(stale, 'verification')).not.toContain('invisible');
		expect(feedbackTag(stale, 'verification')).toContain('aria-hidden="false"');
		expect(stale).toContain('dati precedenti, non modificabili');
		read.mockResolvedValueOnce({ ...decks.getState().data!, preparation_version: 3 });
		expect(await decks.reload()).toBe(true);
		const after = render(DraftDecks, { props: { store, decks } }).body;
		expect(feedbackTag(after, 'verification')).toContain('invisible');
		expect(feedbackTag(after, 'verification')).toContain('aria-hidden="true"');
		expect(read).toHaveBeenCalledTimes(2);
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
