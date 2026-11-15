import { describe, expect, it, vi } from 'vitest';
import { ApiError } from '../api';
import { fetchDraft, fetchDraftDeck, fetchDrafts, openDraft, sendDraftCommand } from './draft-api';
import type { DraftCommands, DraftRead } from './draft-types';

function snapshot(): DraftRead {
	return {
		id: 1,
		championship_id: 7,
		version: 2,
		phase: 'attendance',
		first_race: true,
		can_manage: true,
		my_pilot_ids: [11],
		participants: [{ pilot_id: 11, name: 'Anna', present: true }],
		order: [],
		cards: [],
		picks: [],
		preview_slot_id: null,
		ready: [],
		current_pilot_id: null
	};
}

function response(body: unknown, status = 200): Response {
	return new Response(status === 204 ? null : JSON.stringify(body), {
		status,
		headers: { 'Content-Type': 'application/json' }
	});
}

describe('client draft autenticato', () => {
	it('legge elenco, dettaglio e apertura senza cambiare il client condiviso', async () => {
		const f = vi.fn<typeof fetch>();
		f.mockResolvedValueOnce(response([snapshot()]));
		await expect(fetchDrafts(f)).resolves.toEqual([snapshot()]);
		f.mockResolvedValueOnce(response(snapshot()));
		await expect(fetchDraft(1, f)).resolves.toEqual(snapshot());
		f.mockResolvedValueOnce(response(snapshot(), 201));
		await expect(openDraft(7, f)).resolves.toEqual(snapshot());
		expect(f.mock.calls.map(([path]) => path)).toEqual([
			'/api/drafts',
			'/api/drafts/1',
			'/api/championships/7/draft'
		]);
		for (const [, options] of f.mock.calls) expect(options?.credentials).toBe('same-origin');
		expect(f.mock.calls[2][1]?.method).toBe('POST');
	});

	it('legge solo il mazzo del pilota richiesto e rifiuta contesti discordanti', async () => {
		const value = {
			pilot_id: 11,
			preparation_version: 2,
			ready: false,
			inventory_version: 1,
			game_version: 1,
			inventory: [],
			game_deck: []
		};
		const f = vi.fn<typeof fetch>().mockResolvedValue(response(value));
		await expect(fetchDraftDeck(1, 11, f)).resolves.toEqual(value);
		expect(f.mock.calls[0][0]).toBe('/api/drafts/1/pilots/11/deck');
		await expect(fetchDraftDeck(1, 12, f)).rejects.toThrow(TypeError);
		f.mockResolvedValue(response(snapshot()));
		await expect(fetchDraft(2, f)).rejects.toThrow(TypeError);
		await expect(openDraft(8, f)).rejects.toThrow(TypeError);
	});

	const commands: { action: keyof DraftCommands; body: DraftCommands[keyof DraftCommands] }[] = [
		{ action: 'attendance', body: { version: 2, pilot_id: 11, present: false } },
		{ action: 'attendance/confirm', body: { version: 2 } },
		{ action: 'order', body: { version: 2, pilot_ids: [11] } },
		{ action: 'start', body: { version: 2 } },
		{ action: 'preview', body: { version: 2, slot_id: null } },
		{ action: 'choice', body: { version: 2, slot_id: 3 } },
		{
			action: 'deck/move',
			body: { version: 2, pilot_id: 11, path: 'cards/a.webp', to_game: true }
		},
		{ action: 'ready', body: { version: 2, pilot_id: 11, ready: true } },
		{ action: 'already-disputed', body: { version: 2 } },
		{ action: 'cancel', body: { version: 2 } }
	];

	it.each(commands)(
		'invia una sola POST per $action con il payload esatto',
		async ({ action, body }) => {
			const terminal = action === 'ready' || action === 'already-disputed';
			const result = terminal ? { preparation: null, race_id: 9 } : snapshot();
			const f = vi
				.fn<typeof fetch>()
				.mockResolvedValue(response(result, action === 'cancel' ? 204 : 200));
			await expect(sendDraftCommand(1, action, body, f)).resolves.toEqual(
				action === 'cancel' ? undefined : result
			);
			expect(f).toHaveBeenCalledTimes(1);
			expect(f).toHaveBeenCalledWith(
				`/api/drafts/1/${action}`,
				expect.objectContaining({
					method: 'POST',
					credentials: 'same-origin',
					body: JSON.stringify(body)
				})
			);
		}
	);

	it.each([401, 403, 404, 409, 422, 500])('propaga HTTP %s senza retry', async (status) => {
		const f = vi.fn<typeof fetch>().mockResolvedValue(response({ detail: 'Rifiutato' }, status));
		await expect(sendDraftCommand(1, 'start', { version: 2 }, f)).rejects.toBeInstanceOf(ApiError);
		expect(f).toHaveBeenCalledTimes(1);
	});

	it('non ritenta rete interrotta o una risposta di scrittura inutilizzabile', async () => {
		const f = vi.fn<typeof fetch>().mockRejectedValue(new Error('offline'));
		await expect(sendDraftCommand(1, 'start', { version: 2 }, f)).rejects.toMatchObject({
			status: 0
		});
		expect(f).toHaveBeenCalledTimes(1);
		f.mockReset().mockResolvedValue(response({}));
		await expect(sendDraftCommand(1, 'start', { version: 2 }, f)).rejects.toThrow(TypeError);
		expect(f).toHaveBeenCalledTimes(1);
	});

	it('rifiuta input invalidi prima della rete e non converte numeri o booleani', async () => {
		const f = vi.fn<typeof fetch>();
		for (const id of [0, -1, 1.5, NaN, Infinity, Number.MAX_SAFE_INTEGER + 1]) {
			await expect(fetchDraft(id, f)).rejects.toThrow(RangeError);
		}
		await expect(sendDraftCommand(1, 'start', { version: 0 }, f)).rejects.toThrow(RangeError);
		await expect(
			sendDraftCommand(1, 'order', { version: 2, pilot_ids: [11, 11] }, f)
		).rejects.toThrow(TypeError);
		const extra = { version: 2, unexpected: true };
		await expect(sendDraftCommand(1, 'start', extra, f)).rejects.toThrow(TypeError);
		expect(f).not.toHaveBeenCalled();
	});

	it('conserva liste vuote e rifiuta duplicati o payload lista mancanti', async () => {
		const f = vi.fn<typeof fetch>().mockResolvedValue(response([]));
		await expect(fetchDrafts(f)).resolves.toEqual([]);
		f.mockResolvedValue(response([snapshot(), snapshot()]));
		await expect(fetchDrafts(f)).rejects.toThrow(TypeError);
		f.mockResolvedValue(response(null));
		await expect(fetchDrafts(f)).rejects.toThrow(TypeError);
	});
});
