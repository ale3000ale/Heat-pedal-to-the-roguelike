import { describe, expect, it } from 'vitest';
import {
	enrolledChampionshipIds,
	groupChampionships,
	initiallyOpenGroup
} from './championship-groups';
import type { Championship, Pilot } from './types';

function championship(id: number, isClosed = false): Championship {
	return { id, name: `Campionato ${id}`, date: '2026-01-01', is_closed: isClosed, pilots_count: 0 };
}

function pilot(id: number, championshipId: number | null): Pilot {
	return {
		id,
		name: `Pilota ${id}`,
		team_id: 1,
		gold: 0,
		sponsor: 0,
		point: 0,
		championship:
			championshipId === null ? null : { id: championshipId, name: `Campionato ${championshipId}` }
	};
}

describe('enrolledChampionshipIds', () => {
	it('ignora i piloti senza campionato e non ripete gli id', () => {
		const ids = enrolledChampionshipIds([pilot(1, 10), pilot(2, 10), pilot(3, null)]);
		expect([...ids]).toEqual([10]);
	});
});

describe('groupChampionships', () => {
	it('mette in Iscritto solo gli attivi con un pilota iscritto', () => {
		const groups = groupChampionships([championship(1), championship(2)], [pilot(1, 2)]);
		expect(groups.enrolled.map((c) => c.id)).toEqual([2]);
	});

	it('non ripete in Attivi i campionati già in Iscritto', () => {
		const groups = groupChampionships([championship(1), championship(2)], [pilot(1, 2)]);
		expect(groups.active.map((c) => c.id)).toEqual([1]);
	});

	it('mette in Chiusi tutti i chiusi, anche quelli a cui si partecipava', () => {
		const groups = groupChampionships(
			[championship(1, true), championship(2, true), championship(3)],
			[pilot(1, 1)]
		);
		expect(groups.closed.map((c) => c.id)).toEqual([1, 2]);
		expect(groups.enrolled).toEqual([]);
	});

	it('senza piloti iscritti lascia Iscritto vuoto e tutti gli attivi in Attivi', () => {
		const groups = groupChampionships([championship(1), championship(2)], [pilot(1, null)]);
		expect(groups.enrolled).toEqual([]);
		expect(groups.active.map((c) => c.id)).toEqual([1, 2]);
	});
});

describe('initiallyOpenGroup', () => {
	it('apre Iscritto se c\'è almeno un pilota iscritto', () => {
		const groups = groupChampionships([championship(1)], [pilot(1, 1)]);
		expect(initiallyOpenGroup(groups)).toBe('enrolled');
	});

	it('apre Attivi se nessun pilota è iscritto', () => {
		const groups = groupChampionships([championship(1)], []);
		expect(initiallyOpenGroup(groups)).toBe('active');
	});
});
