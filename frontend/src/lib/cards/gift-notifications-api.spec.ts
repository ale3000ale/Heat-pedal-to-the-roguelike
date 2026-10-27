import { describe, expect, it, vi } from 'vitest';
import { ApiError } from '../api';
import type { CardGift } from './card-play-types';
import {
	acknowledgeGiftNotifications,
	fetchGiftNotifications,
	type PilotGiftNotification
} from './gift-notifications-api';

function gift(id: number): CardGift {
	return {
		id,
		race_id: 7,
		card_name: 'Sponsor',
		card_path: 'cards/sponsor.webp',
		created_at: '2026-10-20T18:00:00'
	};
}

function notification(id: number, pilotId = 1): PilotGiftNotification {
	return { pilotId, gift: gift(id) };
}

function response(status: number, body?: unknown): Response {
	return new Response(body === undefined ? null : JSON.stringify(body), {
		status,
		headers: { 'Content-Type': 'application/json' }
	});
}

function requestBodies(f: ReturnType<typeof vi.fn<typeof fetch>>) {
	return f.mock.calls.map(([, init]) => {
		return JSON.parse(String(init?.body)) as { pilot_id: number; gift_ids: number[] };
	});
}

describe('fetchGiftNotifications', () => {
	it('associa ogni regalo al pilota della richiesta, senza modificare il DTO', async () => {
		const f = vi.fn<typeof fetch>();
		f.mockResolvedValueOnce(response(200, [gift(10)]));
		f.mockResolvedValueOnce(response(200, [gift(20)]));
		const found = await fetchGiftNotifications(3, [1, 2, 1], f);
		expect(found).toEqual([notification(10, 1), notification(20, 2)]);
		expect(f).toHaveBeenCalledTimes(2);
		expect(f.mock.calls.map(([url]) => url)).toEqual([
			'/api/championships/3/card-gifts?pilot_id=1',
			'/api/championships/3/card-gifts?pilot_id=2'
		]);
	});

	it('propaga un errore parziale invece di produrre uno snapshot incompleto', async () => {
		const f = vi.fn<typeof fetch>();
		f.mockResolvedValueOnce(response(200, [gift(10)]));
		f.mockResolvedValueOnce(response(500, { detail: 'Lettura fallita' }));
		await expect(fetchGiftNotifications(3, [1, 2], f)).rejects.toMatchObject({
			status: 500,
			message: 'Lettura fallita'
		});
	});

	it('non nasconde il 401 al coordinatore live', async () => {
		const f = vi.fn<typeof fetch>().mockResolvedValue(response(401));
		await expect(fetchGiftNotifications(3, [1], f)).rejects.toBeInstanceOf(ApiError);
	});

	it('non legge senza piloti e valida tutti gli ID prima della rete', async () => {
		const f = vi.fn<typeof fetch>();
		await expect(fetchGiftNotifications(3, [], f)).resolves.toEqual([]);
		await expect(fetchGiftNotifications(3, [1, 0], f)).rejects.toBeInstanceOf(RangeError);
		expect(f).not.toHaveBeenCalled();
	});
});

describe('acknowledgeGiftNotifications', () => {
	it('invia solo lo snapshot mostrato, separato per pilota e senza duplicati', async () => {
		const f = vi.fn<typeof fetch>().mockResolvedValue(response(204));
		const displayed = [notification(10), notification(10), notification(20, 2)];
		const before = structuredClone(displayed);
		await acknowledgeGiftNotifications(3, displayed, f);
		expect(requestBodies(f)).toEqual([
			{ pilot_id: 1, gift_ids: [10] },
			{ pilot_id: 2, gift_ids: [20] }
		]);
		expect(f).toHaveBeenCalledWith(
			'/api/championships/3/card-gifts/seen-selected',
			expect.objectContaining({ method: 'POST', credentials: 'same-origin' })
		);
		expect(displayed).toEqual(before);
	});

	it('suddivide 201 ID in batch da 100, 100 e 1', async () => {
		const f = vi.fn<typeof fetch>().mockResolvedValue(response(204));
		const displayed = Array.from({ length: 201 }, (_, index) => notification(index + 1));
		await acknowledgeGiftNotifications(3, displayed, f);
		const bodies = requestBodies(f);
		expect(bodies.map((body) => body.gift_ids.length)).toEqual([100, 100, 1]);
		expect(bodies.flatMap((body) => body.gift_ids)).toEqual(displayed.map(({ gift }) => gift.id));
	});

	it('non chiama nessun endpoint con uno snapshot vuoto', async () => {
		const f = vi.fn<typeof fetch>();
		await acknowledgeGiftNotifications(3, [], f);
		expect(f).not.toHaveBeenCalled();
	});

	it('rifiuta tutti gli ID non sicuri prima di confermare qualsiasi pilota', async () => {
		const f = vi.fn<typeof fetch>();
		for (const id of [0, -1, 1.5, NaN, Infinity, Number.MAX_SAFE_INTEGER + 1]) {
			await expect(
				acknowledgeGiftNotifications(3, [notification(10), notification(id, 2)], f)
			).rejects.toBeInstanceOf(RangeError);
		}
		await expect(acknowledgeGiftNotifications(3, [notification(10, 0)], f)).rejects.toBeInstanceOf(
			RangeError
		);
		await expect(acknowledgeGiftNotifications(0, [], f)).rejects.toBeInstanceOf(RangeError);
		expect(f).not.toHaveBeenCalled();
	});

	it('si ferma al primo batch fallito senza inviare quelli successivi', async () => {
		const f = vi.fn<typeof fetch>();
		f.mockResolvedValueOnce(response(204));
		f.mockResolvedValueOnce(response(503));
		const displayed = Array.from({ length: 201 }, (_, index) => notification(index + 1));
		await expect(acknowledgeGiftNotifications(3, displayed, f)).rejects.toMatchObject({
			status: 503
		});
		expect(f).toHaveBeenCalledTimes(2);
	});
});
