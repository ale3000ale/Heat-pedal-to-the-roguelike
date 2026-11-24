import { afterEach, describe, expect, it, vi } from 'vitest';
import { boardPoolImageUrl, updateBoardPoolCard } from './board-pool-api';

afterEach(() => vi.unstubAllGlobals());

describe('pool di mappe ed eventi', () => {
	it('costruisce l URL servito da media', () => {
		expect(boardPoolImageUrl('board/maps/DEUTSCHLAND.webp')).toBe(
			'/media/board/maps/DEUTSCHLAND.webp'
		);
		expect(boardPoolImageUrl('board\\events\\AFFLUENZA RECORD.webp')).toBe(
			'/media/board/events/AFFLUENZA RECORD.webp'
		);
	});

	it('invia la modifica di una carta con PATCH', async () => {
		const fetch = vi.fn().mockResolvedValue(
			new Response(
				JSON.stringify({
					id: 3,
					nome: 'Mappa 3',
					image: 'board/maps/mappa-3.webp',
					in_pool: true,
					blocked: true,
					fields: []
				}),
				{ status: 200, headers: { 'Content-Type': 'application/json' } }
			)
		);
		vi.stubGlobal('fetch', fetch);

		const card = await updateBoardPoolCard(7, 'mappe', 3, { blocked: true });

		expect(card.blocked).toBe(true);
		expect(fetch).toHaveBeenCalledWith(
			'/api/championships/7/board-pools/mappe/cards/3',
			expect.objectContaining({ method: 'PATCH', body: JSON.stringify({ blocked: true }) })
		);
	});
});
