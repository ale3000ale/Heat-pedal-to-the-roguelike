import { describe, expect, it } from 'vitest';
import { standingKey } from './standings';
import type { Standing } from './race-types';

function row(rank: number, pilot_id: number | null, points = 10): Standing {
	return { rank, pilot_id, pilot_name: `pilota ${pilot_id ?? 'x'}`, points, races_played: 1 };
}

function keys(rows: Standing[]): string[] {
	return rows.map((r, i) => standingKey(r, i));
}

describe('standingKey', () => {
	it('dà chiavi diverse a due piloti a pari merito', () => {
		const result = keys([row(1, 7), row(2, 3), row(2, 5)]);
		expect(new Set(result).size).toBe(3);
	});

	it('resta uguale se la classifica cambia ordine', () => {
		const a = standingKey(row(1, 7), 0);
		const b = standingKey(row(2, 7), 1);
		expect(a).toBe(b);
	});

	it('regge più piloti senza id a pari merito (campionato chiuso)', () => {
		const result = keys([row(1, null), row(1, null), row(3, null)]);
		expect(new Set(result).size).toBe(3);
	});

	it('non confonde un id con una chiave di riserva', () => {
		const result = keys([row(1, 1), row(1, null)]);
		expect(new Set(result).size).toBe(2);
	});
});
