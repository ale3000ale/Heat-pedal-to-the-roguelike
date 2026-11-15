import { describe, expect, it, vi } from 'vitest';
import { ApiError } from '../../api';
import { fetchAdminChampionshipPilots, fetchAdminPilotCards } from './admin-pilot-cards-api';
import type { AdminPilotCardsRead, AdminPilotRead } from './admin-pilot-cards-types';

const pilot: AdminPilotRead = { pilot_id: 11, name: 'Anna', user_id: 5, username: 'mario' };

function snapshot(): AdminPilotCardsRead {
	return {
		championship_id: 7,
		pilot: { ...pilot },
		read_only: true,
		blocked_reason: 'Campionato chiuso',
		containers: {
			game_deck: {
				available: true,
				id: 1,
				version: 2,
				cards: [{ name: 'Velocità 1', path: 'cards/starter/velocita-1.webp', copies: 3 }]
			},
			modification_inventory: { available: true, id: 2, version: 1, cards: [] },
			sponsor_inventory: { available: true, id: 3, version: 1, cards: [] },
			modification_pool: { available: true, id: 4, version: 5, cards: [] },
			sponsor_pool: { available: false, id: null, version: null, cards: [] }
		}
	};
}

function response(status: number, body: unknown): Response {
	return new Response(JSON.stringify(body), {
		status,
		headers: { 'Content-Type': 'application/json' }
	});
}

describe('letture admin dei piloti e delle carte', () => {
	it('legge gli iscritti con username mediante una sola GET autenticata', async () => {
		const f = vi.fn<typeof fetch>().mockResolvedValue(response(200, [pilot]));
		await expect(fetchAdminChampionshipPilots(7, f)).resolves.toEqual([pilot]);
		expect(f).toHaveBeenCalledTimes(1);
		expect(f).toHaveBeenCalledWith(
			'/api/admin/championships/7/pilots',
			expect.objectContaining({ method: 'GET', credentials: 'same-origin', body: undefined })
		);
	});

	it('conserva un elenco vuoto senza inventare iscritti', async () => {
		const f = vi.fn<typeof fetch>().mockResolvedValue(response(200, []));
		await expect(fetchAdminChampionshipPilots(7, f)).resolves.toEqual([]);
	});

	it('conserva carte, versioni, blocchi e distinzione tra pool vuota e assente', async () => {
		const body = snapshot();
		const f = vi.fn<typeof fetch>().mockResolvedValue(response(200, body));
		const result = await fetchAdminPilotCards(7, 11, f);
		expect(result).toEqual(body);
		expect(result.containers.modification_pool.available).toBe(true);
		expect(result.containers.sponsor_pool.available).toBe(false);
		expect(f).toHaveBeenCalledTimes(1);
		expect(f).toHaveBeenCalledWith(
			'/api/admin/championships/7/pilots/11/cards',
			expect.objectContaining({ method: 'GET', credentials: 'same-origin', body: undefined })
		);
	});

	it.each([401, 403, 404, 409])('propaga HTTP %s senza fallback o retry', async (status) => {
		const f = vi.fn<typeof fetch>().mockResolvedValue(response(status, { detail: 'Rifiutato' }));
		await expect(fetchAdminPilotCards(7, 11, f)).rejects.toBeInstanceOf(ApiError);
		expect(f).toHaveBeenCalledTimes(1);
	});

	it.each([0, -1, 1.5, NaN, Infinity, Number.MAX_SAFE_INTEGER + 1])(
		'rifiuta ID non valido %s prima della rete',
		async (id) => {
			const f = vi.fn<typeof fetch>();
			await expect(fetchAdminChampionshipPilots(id, f)).rejects.toBeInstanceOf(RangeError);
			await expect(fetchAdminPilotCards(7, id, f)).rejects.toBeInstanceOf(RangeError);
			await expect(fetchAdminPilotCards(id, 11, f)).rejects.toBeInstanceOf(RangeError);
			expect(f).not.toHaveBeenCalled();
		}
	);

	it.each(['campionato', 'pilota'])('rifiuta uno snapshot di un altro %s', async (context) => {
		const body = snapshot();
		if (context === 'campionato') body.championship_id = 8;
		else body.pilot.pilot_id = 12;
		const f = vi.fn<typeof fetch>().mockResolvedValue(response(200, body));
		await expect(fetchAdminPilotCards(7, 11, f)).rejects.toThrow(
			'La risposta delle carte non corrisponde al campionato e pilota richiesti'
		);
	});
});
