import { describe, expect, it } from 'vitest';
import { canShowEnroll, enrollablePilots } from './enroll-candidates';
import type { Pilot } from '../types';

function pilot(id: number, teamId: number | null, championshipId: number | null = null): Pilot {
	return {
		id,
		name: `Pilota ${id}`,
		team_id: teamId,
		gold: 0,
		sponsor: 0,
		point: 0,
		championship:
			championshipId === null ? null : { id: championshipId, name: `Campionato ${championshipId}` }
	};
}

describe('enrollablePilots', () => {
	it('tiene i piloti con un team e senza campionato attivo', () => {
		const result = enrollablePilots([pilot(1, 1), pilot(2, 1)]);
		expect(result.map((p) => p.id)).toEqual([1, 2]);
	});

	it('esclude i piloti senza team', () => {
		const result = enrollablePilots([pilot(1, null), pilot(2, 1)]);
		expect(result.map((p) => p.id)).toEqual([2]);
	});

	it('esclude i piloti già iscritti a un campionato attivo, anche a un altro', () => {
		const result = enrollablePilots([pilot(1, 1, 7), pilot(2, 1, 8), pilot(3, 1)]);
		expect(result.map((p) => p.id)).toEqual([3]);
	});

	it('senza piloti restituisce un elenco vuoto', () => {
		expect(enrollablePilots([])).toEqual([]);
	});
});

describe('canShowEnroll', () => {
	it('mostra il pulsante in un campionato attivo senza piloti iscritti', () => {
		expect(canShowEnroll(false, 0)).toBe(true);
	});

	it('lo nasconde in un campionato chiuso', () => {
		expect(canShowEnroll(true, 0)).toBe(false);
	});

	it("lo nasconde se c'è già un pilota iscritto", () => {
		expect(canShowEnroll(false, 1)).toBe(false);
	});

	it('lo nasconde in un campionato chiuso anche con un pilota iscritto', () => {
		expect(canShowEnroll(true, 2)).toBe(false);
	});
});
