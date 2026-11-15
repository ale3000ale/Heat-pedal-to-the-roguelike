import { describe, expect, it, vi } from 'vitest';
import { createRawSnippet } from 'svelte';
import { render } from 'svelte/server';
import Modal from './components/modal.svelte';
import DraftModal from './components/draft-modal.svelte';
import type { DraftRead } from './draft-types';
import { DraftStore } from './stores/draft.svelte';

function content(rows = 1) {
	return createRawSnippet(() => ({
		render: () => `<div>${'<p>Contenuto di prova</p>'.repeat(rows)}</div>`
	}));
}

/** Isola gli attributi del dialog SSR; non legge CSS calcolato o geometrie. */
function dialogTag(body: string): string {
	const tag = body.match(/<div\b[^>]*role="dialog"[^>]*>/)?.[0];
	if (!tag) throw new Error('Dialog assente');
	return tag;
}

async function setup(phase: DraftRead['phase']) {
	const value: DraftRead = {
		id: 1,
		championship_id: 7,
		version: 2,
		phase,
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
	const read = vi.fn<() => Promise<DraftRead>>().mockResolvedValue(value);
	const send = vi.fn();
	const store = new DraftStore({ draftId: 1, getContext: () => 'auth-1', read, send });
	await store.refresh();
	return { store, read, send };
}

// Solo SSR: nessun clic, resize, misura delle altezze o mantenimento scrollTop provato.
describe('viewport stabile del modal draft', () => {
	it('conserva il layout predefinito degli altri modal', () => {
		const body = render(Modal, {
			props: { open: true, title: 'Altro modal', children: content() }
		}).body;
		expect(dialogTag(body)).not.toContain('viewport-stable');
		expect(dialogTag(body)).toContain('max-h-[90vh]');
		expect(dialogTag(body)).toContain('overflow-y-auto');
	});

	it.each([1, 30])('attiva la modalita solo su richiesta con %s righe', (rows) => {
		const body = render(Modal, {
			props: { open: true, title: 'Prova', stableViewport: true, children: content(rows) }
		}).body;
		expect(dialogTag(body)).toContain('viewport-stable');
		expect(dialogTag(body)).toContain('overflow-y-auto');
		expect(body).toContain('Contenuto di prova');
	});

	it.each(['attendance', 'order', 'picking', 'decks'] as const)(
		'abilita il viewport stabile solo nelle fasi carte/mazzi: %s',
		async (phase) => {
			const { store, read, send } = await setup(phase);
			const body = render(DraftModal, { props: { store, children: content() } }).body;
			expect(dialogTag(body).includes('viewport-stable')).toBe(
				phase === 'picking' || phase === 'decks'
			);
			expect(dialogTag(body)).toContain('aria-modal="true"');
			expect(read).toHaveBeenCalledTimes(1);
			expect(send).not.toHaveBeenCalled();
		}
	);

	it('non renderizza un modal chiuso anche con viewport stabile', () => {
		const body = render(Modal, {
			props: { open: false, title: 'Prova', stableViewport: true, children: content() }
		}).body;
		expect(body).not.toContain('role="dialog"');
	});

	it('conserva showClose indipendente dall opzione di layout', () => {
		const body = render(Modal, {
			props: {
				open: true,
				title: 'Prova',
				stableViewport: true,
				showClose: false,
				children: content()
			}
		}).body;
		// Resta solo il pulsante sfondo, non la X nell'intestazione.
		expect(body.match(/aria-label="Chiudi"/g)).toHaveLength(1);
	});
});
