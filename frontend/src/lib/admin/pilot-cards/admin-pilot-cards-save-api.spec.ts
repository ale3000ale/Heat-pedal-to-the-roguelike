import { describe, expect, it, vi } from 'vitest';
import { ApiError } from '../../api';
import { AdminCardSaveResponseError, saveAdminPilotCards } from './admin-pilot-cards-save-api';
import type { AdminPilotCardsSave } from './admin-pilot-cards-save-types';
import type { AdminPilotCardsRead } from './admin-pilot-cards-types';

const path = 'cards/turbo.webp';

function request(): AdminPilotCardsSave {
	return {
		versions: {
			game_deck: { id: 1, version: 3 },
			modification_inventory: { id: 2, version: 3 },
			sponsor_inventory: { id: 3, version: 3 },
			modification_pool: { id: 4, version: 3 },
			sponsor_pool: null
		},
		transfers: [{ source: 'game_deck', path }]
	};
}

function snapshot(): AdminPilotCardsRead {
	return {
		championship_id: 7,
		pilot: { pilot_id: 11, name: 'Anna', user_id: 5, username: 'mario' },
		read_only: false,
		blocked_reason: null,
		containers: {
			game_deck: {
				available: true,
				id: 1,
				version: 4,
				cards: [{ name: 'Turbo', path, copies: 1 }]
			},
			modification_inventory: { available: true, id: 2, version: 3, cards: [] },
			sponsor_inventory: { available: true, id: 3, version: 3, cards: [] },
			modification_pool: {
				available: true,
				id: 4,
				version: 4,
				cards: [{ name: 'Turbo', path, copies: 1 }]
			},
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

describe('trasporto PUT delle carte admin', () => {
	it('invia una sola PUT autenticata con il contratto completo e senza GET', async () => {
		const input = request();
		const before = structuredClone(input);
		const body = snapshot();
		const f = vi.fn<typeof fetch>().mockResolvedValue(response(200, body));
		await expect(saveAdminPilotCards(7, 11, input, f)).resolves.toEqual(body);
		expect(f).toHaveBeenCalledTimes(1);
		expect(f).toHaveBeenCalledWith('/api/admin/championships/7/pilots/11/cards', {
			method: 'PUT',
			credentials: 'same-origin',
			headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
			body: JSON.stringify(before)
		});
		expect(input).toEqual(before);
	});

	it('restituisce le versioni server senza sovrascrivere quelle attese o creare pool', async () => {
		const input = request();
		const f = vi.fn<typeof fetch>().mockResolvedValue(response(200, snapshot()));
		const result = await saveAdminPilotCards(7, 11, input, f);
		expect(result.containers.game_deck.version).toBe(4);
		expect(input.versions.game_deck.version).toBe(3);
		expect(input.versions.sponsor_pool).toBeNull();
		expect(result.containers.sponsor_pool.available).toBe(false);
		expect(f).toHaveBeenCalledTimes(1);
	});

	it.each([401, 403, 404, 409, 422, 500])(
		'propaga HTTP %s senza retry o scarto degli input',
		async (status) => {
			const input = request();
			const before = structuredClone(input);
			const f = vi.fn<typeof fetch>().mockResolvedValue(response(status, { detail: 'Rifiutato' }));
			const result = saveAdminPilotCards(7, 11, input, f);
			await expect(result).rejects.toBeInstanceOf(ApiError);
			await expect(result).rejects.toMatchObject({ status, message: 'Rifiutato' });
			expect(f).toHaveBeenCalledTimes(1);
			expect(input).toEqual(before);
		}
	);

	it('propaga un errore di rete senza ritentare o rileggere', async () => {
		const input = request();
		const before = structuredClone(input);
		const f = vi.fn<typeof fetch>().mockRejectedValue(new Error('Connessione interrotta'));
		await expect(saveAdminPilotCards(7, 11, input, f)).rejects.toMatchObject({
			name: 'ApiError',
			status: 0
		});
		expect(f).toHaveBeenCalledTimes(1);
		expect(input).toEqual(before);
	});

	it.each([0, -1, 1.5, NaN, Infinity, Number.MAX_SAFE_INTEGER + 1])(
		'rifiuta ID invalido %s prima della rete',
		async (id) => {
			const f = vi.fn<typeof fetch>();
			await expect(saveAdminPilotCards(id, 11, request(), f)).rejects.toBeInstanceOf(RangeError);
			await expect(saveAdminPilotCards(7, id, request(), f)).rejects.toBeInstanceOf(RangeError);
			expect(f).not.toHaveBeenCalled();
		}
	);

	it.each(['campionato', 'pilota'])(
		'segnala una risposta di altro %s senza un secondo invio',
		async (context) => {
			const body = snapshot();
			if (context === 'campionato') body.championship_id = 8;
			else body.pilot.pilot_id = 12;
			const input = request();
			const before = structuredClone(input);
			const f = vi.fn<typeof fetch>().mockResolvedValue(response(200, body));
			await expect(saveAdminPilotCards(7, 11, input, f)).rejects.toBeInstanceOf(
				AdminCardSaveResponseError
			);
			expect(f).toHaveBeenCalledTimes(1);
			expect(input).toEqual(before);
		}
	);

	it('segnala JSON illeggibile senza fingere un rollback o ritentare', async () => {
		const f = vi.fn<typeof fetch>().mockResolvedValue(new Response('non-json', { status: 200 }));
		await expect(saveAdminPilotCards(7, 11, request(), f)).rejects.toThrow(
			'il server potrebbe avere applicato le modifiche'
		);
		expect(f).toHaveBeenCalledTimes(1);
	});

	it('non accetta un 204 al posto dello snapshot previsto', async () => {
		const f = vi.fn<typeof fetch>().mockResolvedValue(new Response(null, { status: 204 }));
		await expect(saveAdminPilotCards(7, 11, request(), f)).rejects.toBeInstanceOf(
			AdminCardSaveResponseError
		);
		expect(f).toHaveBeenCalledTimes(1);
	});
});
