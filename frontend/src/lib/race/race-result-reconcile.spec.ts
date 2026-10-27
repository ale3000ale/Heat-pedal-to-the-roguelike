import { describe, expect, it } from 'vitest';
import { hasResultChanges, reconcileResults, type ResultForm } from './race-result-reconcile';

function baseForm(): ResultForm {
	return {
		order: [
			{ pilot_id: 1, name: 'Uno', sponsor: 1 },
			{ pilot_id: 2, name: 'Due', sponsor: 2 }
		],
		absent: [{ pilot_id: 3, name: 'Tre' }]
	};
}

function ids(form: ResultForm) {
	return [...form.order, ...form.absent].map((row) => row.pilot_id);
}

describe('riconciliazione risultati', () => {
	it('adotta il remoto se non ci sono modifiche e non muta gli input', () => {
		const base = baseForm();
		const local = structuredClone(base);
		const remote = structuredClone(base);
		remote.order.reverse();
		remote.order[0].sponsor = 8;
		const before = structuredClone([base, local, remote]);
		const merged = reconcileResults(base, local, remote);
		expect(merged.form).toEqual(remote);
		expect(merged.hasChanges).toBe(false);
		expect([base, local, remote]).toEqual(before);
		merged.form.order[0].sponsor = 99;
		expect(remote.order[0].sponsor).toBe(8);
	});

	it('conserva sponsor locali ma aggiorna ordine e sponsor non modificati', () => {
		const base = baseForm();
		const local = structuredClone(base);
		local.order[0].sponsor = 5;
		const remote = structuredClone(base);
		remote.order.reverse();
		remote.order[0].sponsor = 8;
		const merged = reconcileResults(base, local, remote);
		expect(merged.form.order.map((row) => row.sponsor)).toEqual([8, 5]);
		expect(merged.assignmentKept).toBe(false);
		expect(merged.hasChanges).toBe(true);
	});

	it('preserva ordine e assenti insieme senza duplicare un pilota', () => {
		const base = baseForm();
		const local = structuredClone(base);
		local.order.reverse();
		const remote = structuredClone(base);
		remote.absent = [{ pilot_id: 2, name: 'Due' }];
		remote.order[1] = { pilot_id: 3, name: 'Tre', sponsor: 4 };
		const merged = reconcileResults(base, local, remote);
		expect(merged.form.order.map((row) => row.pilot_id)).toEqual([2, 1]);
		expect(merged.form.absent).toEqual(local.absent);
		expect(new Set(ids(merged.form)).size).toBe(ids(merged.form).length);
		expect(merged.conflict).toBe(true);
	});

	it('preserva anche una modifica locale alla sola lista assenti', () => {
		const base = baseForm();
		const local = structuredClone(base);
		local.absent = [];
		const remote = structuredClone(base);
		remote.order.reverse();
		const merged = reconcileResults(base, local, remote);
		expect(merged.form.absent).toEqual([]);
		expect(merged.form.order.map((row) => row.pilot_id)).toEqual([1, 2]);
	});

	it('non perde uno sponsor locale se il server sposta il pilota tra gli assenti', () => {
		const base = baseForm();
		const local = structuredClone(base);
		local.order[0].sponsor = 9;
		const remote = structuredClone(base);
		remote.order.shift();
		remote.absent.push({ pilot_id: 1, name: 'Uno' });
		const merged = reconcileResults(base, local, remote);
		expect(merged.form.order[0].sponsor).toBe(9);
		expect(merged.form.absent).toEqual(local.absent);
		expect(merged.conflict).toBe(true);
	});

	it('conserva input vuoto e segnala modifiche sponsor concorrenti', () => {
		const base = baseForm();
		const local = structuredClone(base);
		local.order[0].sponsor = undefined;
		const remote = structuredClone(base);
		remote.order[0].sponsor = 6;
		const merged = reconcileResults(base, local, remote);
		expect(merged.form.order[0].sponsor).toBeUndefined();
		expect(merged.conflict).toBe(true);
		local.order[0].sponsor = 6;
		expect(reconcileResults(base, local, remote).hasChanges).toBe(false);
	});

	it('puo usare la bozza inviata come base per preservare modifiche durante PUT', () => {
		const submitted = baseForm();
		const local = structuredClone(submitted);
		local.order[0].sponsor = 7;
		const response = structuredClone(submitted);
		response.order[1].sponsor = 4;
		const merged = reconcileResults(submitted, local, response);
		expect(merged.form.order.map((row) => row.sponsor)).toEqual([7, 4]);
	});

	it('ignora nomi e ordine degli assenti nel confronto ma rifiuta duplicati', () => {
		const base = baseForm();
		const local = structuredClone(base);
		local.order[0].name = 'Nome aggiornato';
		expect(hasResultChanges(base, local)).toBe(false);
		local.absent.push({ pilot_id: 1, name: 'Uno' });
		expect(() => reconcileResults(base, local, base)).toThrow(RangeError);
	});
});
