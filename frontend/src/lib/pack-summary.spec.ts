import { describe, expect, it } from 'vitest';
import { groupByCard } from './pack-summary';

const a = { card: { path: '/a.webp' }, section: 'modifiche' };
const b = { card: { path: '/b.webp' }, section: 'modifiche' };
const sponsorA = { card: { path: '/a.webp' }, section: 'sponsor' };

describe('groupByCard', () => {
	it('restituisce una lista vuota senza carte', () => {
		expect(groupByCard([])).toEqual([]);
	});

	it("conta le copie e mantiene l'ordine della prima uscita", () => {
		const result = groupByCard([a, b, a, a]);
		expect(result.map((g) => g.entry.card.path)).toEqual(['/a.webp', '/b.webp']);
		expect(result.map((g) => g.copies)).toEqual([3, 1]);
	});

	it('non unisce carte con lo stesso percorso in sezioni diverse', () => {
		const result = groupByCard([a, sponsorA]);
		expect(result).toHaveLength(2);
	});
});
