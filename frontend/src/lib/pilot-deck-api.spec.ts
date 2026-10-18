import { describe, expect, it, vi } from 'vitest';
import { fetchPilotGameDeck } from './pilot-deck-api';

function jsonResponse(status: number, body: unknown): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { 'Content-Type': 'application/json' }
	});
}

describe('fetchPilotGameDeck', () => {
	it('restituisce il game_deck del dettaglio del pilota', async () => {
		const detail = {
			id: 7,
			name: 'Alex',
			team_id: null,
			deleted: false,
			inventory: [],
			sponsor_inventory: [],
			game_deck: [{ name: 'Freno', path: 'cards/base/modifiche/freno.webp', copies: 2 }],
			championship: null
		};
		const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, detail));
		const result = await fetchPilotGameDeck(7, fetchMock);
		expect(result).toEqual(detail.game_deck);
		expect(fetchMock.mock.calls[0][0]).toBe('/api/pilots/7');
	});

	it('propaga gli errori del backend', async () => {
		const fetchMock = vi
			.fn()
			.mockResolvedValue(jsonResponse(404, { detail: 'Pilota inesistente' }));
		await expect(fetchPilotGameDeck(99, fetchMock)).rejects.toThrow('Pilota inesistente');
	});
});
