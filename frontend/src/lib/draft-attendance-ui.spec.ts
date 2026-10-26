import { describe, expect, it, vi } from 'vitest';
import { render } from 'svelte/server';
import DraftStart from './components/draft-start.svelte';
import DraftAttendance from './components/draft-attendance.svelte';
import type { DraftSessionOptions } from './draft-session';
import type { DraftRead } from './draft-types';
import { DraftStore } from './stores/draft.svelte';

function snapshot(): DraftRead {
	return {
		id: 1,
		championship_id: 7,
		version: 2,
		phase: 'attendance',
		first_race: true,
		can_manage: true,
		my_pilot_ids: [11],
		participants: [
			{ pilot_id: 11, name: 'Anna', present: true },
			{ pilot_id: 12, name: 'Luca', present: false }
		],
		order: [],
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

// Verifiche SSR predisposte: non sono clic, test di tastiera o prove browser.

describe('rendering iniziale e presenze draft', () => {
	it('mostra i due percorsi senza inviare richieste nel rendering', async () => {
		const { store, read, send } = await setup();
		const ondraft = vi.fn();
		const { body } = render(DraftStart, { props: { store, ondraft } });
		expect(body).toContain('Gara già disputata');
		expect(body).toContain('Draft');
		expect(body).toContain('type="button"');
		expect(read).toHaveBeenCalledTimes(1);
		expect(send).not.toHaveBeenCalled();
		expect(ondraft).not.toHaveBeenCalled();
	});

	it('mostra presenti prima degli assenti e i comandi per singolo pilota', async () => {
		const { store, send } = await setup();
		const { body } = render(DraftAttendance, { props: { store } });
		expect(body).toMatch(/Presenti[\s\S]*Anna[\s\S]*Assenti[\s\S]*Luca/);
		expect(body).toContain('aria-label="Escludi Anna"');
		expect(body).toContain('aria-label="Includi Luca"');
		expect(body).toContain('Avanti');
		expect(send).not.toHaveBeenCalled();
	});

	it('non abilita i pulsanti per chi non gestisce la preparazione', async () => {
		const value = snapshot();
		value.can_manage = false;
		const { store } = await setup(value);
		const { body } = render(DraftStart, { props: { store, ondraft: vi.fn() } });
		expect(body).toMatch(/<button[^>]*disabled/);
		const attendance = render(DraftAttendance, { props: { store } }).body;
		expect(attendance).toMatch(/<button[^>]*disabled/);
	});

	it('mostra elenchi vuoti senza inventare piloti e disabilita Avanti', async () => {
		const value = snapshot();
		value.participants = [];
		value.my_pilot_ids = [];
		const { store } = await setup(value);
		const { body } = render(DraftAttendance, { props: { store } });
		expect(body).toContain('Nessun pilota presente.');
		expect(body).toContain('Nessun pilota assente.');
		expect(body).toMatch(/<button[^>]*disabled/);
	});

	it('non rende comandi iniziali dopo il cambio fase', async () => {
		const value = snapshot();
		value.phase = 'order';
		const { store } = await setup(value);
		const start = render(DraftStart, { props: { store, ondraft: vi.fn() } }).body;
		const attendance = render(DraftAttendance, { props: { store } }).body;
		expect(start).not.toContain('Gara già disputata');
		expect(attendance).not.toContain('>Avanti<');
		expect(attendance).not.toContain('aria-label="Escludi Anna"');
	});

	it('tratta i nomi come testo e non come markup eseguibile', async () => {
		const value = snapshot();
		value.participants[0].name = '<script>example</script>';
		const { store } = await setup(value);
		const { body } = render(DraftAttendance, { props: { store } });
		expect(body).not.toContain('<script>example</script>');
		expect(body).toContain('&lt;script');
	});
});
