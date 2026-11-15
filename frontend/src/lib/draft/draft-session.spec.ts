import { describe, expect, it, vi } from 'vitest';
import { ApiError } from '../api';
import { createDraftSession } from './draft-session';
import type { DraftSessionOptions } from './draft-session';
import type { DraftRead } from './draft-types';

function snapshot(version = 2): DraftRead {
	return {
		id: 1,
		championship_id: 7,
		version,
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

function deferred<T>() {
	let resolve!: (value: T) => void;
	const promise = new Promise<T>((done) => {
		resolve = done;
	});
	return { promise, resolve };
}

function setup() {
	let context: string | null = 'auth-1:judge:draft-1';
	const read = vi.fn<NonNullable<DraftSessionOptions['read']>>().mockResolvedValue(snapshot());
	const send = vi.fn<NonNullable<DraftSessionOptions['send']>>().mockResolvedValue(snapshot(3));
	const session = createDraftSession({ draftId: 1, getContext: () => context, read, send });
	return {
		session,
		read,
		send,
		changeContext: (value: string | null) => {
			context = value;
		}
	};
}

describe('sessione draft isolata', () => {
	it('non esegue richieste iniziali o comandi senza snapshot', async () => {
		const { session, read, send } = setup();
		expect(session.getState().status).toBe('empty');
		expect(await session.command('start', {})).toBe(false);
		expect(read).not.toHaveBeenCalled();
		expect(send).not.toHaveBeenCalled();
	});

	it('usa la versione server e restituisce copie indipendenti', async () => {
		const { session, send } = setup();
		expect(await session.refresh()).toBe(true);
		const view = session.getState();
		view.snapshot!.version = 999;
		view.snapshot!.participants[0].name = 'Modificato';
		expect(await session.command('attendance', { pilot_id: 11, present: false })).toBe(true);
		expect(send).toHaveBeenCalledWith(1, 'attendance', {
			version: 2,
			pilot_id: 11,
			present: false
		});
		expect(session.getState().snapshot?.version).toBe(3);
		expect(session.getState().snapshot?.participants[0].name).toBe('Anna');
	});

	it('blocca doppio invio e letture concorrenti alla scrittura', async () => {
		const { session, read, send } = setup();
		await session.refresh();
		const pending = deferred<unknown>();
		send.mockReturnValueOnce(pending.promise);
		const first = session.command('start', {});
		expect(session.getState().status).toBe('writing');
		expect(await session.command('start', {})).toBe(false);
		expect(await session.refresh()).toBe(false);
		expect(send).toHaveBeenCalledTimes(1);
		expect(read).toHaveBeenCalledTimes(1);
		pending.resolve(snapshot(3));
		expect(await first).toBe(true);
	});

	it('non scrive durante una lettura e non accoda richieste implicite', async () => {
		const { session, read, send } = setup();
		const pending = deferred<unknown>();
		read.mockReturnValueOnce(pending.promise);
		const loading = session.refresh();
		expect(await session.refresh()).toBe(false);
		expect(await session.command('start', {})).toBe(false);
		pending.resolve(snapshot());
		await loading;
		expect(read).toHaveBeenCalledTimes(1);
		expect(send).not.toHaveBeenCalled();
	});

	it('mantiene il conflitto fino a rilettura server esplicita', async () => {
		const { session, read, send } = setup();
		await session.refresh();
		send.mockRejectedValueOnce(new ApiError(409, 'Conflitto'));
		expect(await session.command('start', {})).toBe(false);
		expect(session.getState()).toMatchObject({ status: 'blocked', block: 'conflict' });
		expect(session.getState().snapshot?.version).toBe(2);
		expect(await session.command('start', {})).toBe(false);
		expect(read).toHaveBeenCalledTimes(1);
		read.mockResolvedValueOnce(snapshot(4));
		expect(await session.refresh()).toBe(true);
		expect(session.getState()).toMatchObject({ status: 'idle', block: null });
		await session.command('start', {});
		expect(send.mock.calls[1][2].version).toBe(4);
	});

	it('consente correzione manuale dopo 422 senza retry automatici', async () => {
		const { session, send } = setup();
		await session.refresh();
		send.mockRejectedValueOnce(new ApiError(422, 'Movimento non valido'));
		expect(await session.command('start', {})).toBe(false);
		expect(session.getState()).toMatchObject({
			status: 'idle',
			block: null,
			error: 'Movimento non valido'
		});
		expect(send).toHaveBeenCalledTimes(1);
		expect(await session.command('start', {})).toBe(true);
	});

	it.each([
		new ApiError(0, 'Rete interrotta'),
		new ApiError(500, 'Errore server'),
		new TypeError('DTO')
	])('conserva snapshot e blocca gli esiti incerti: %s', async (error) => {
		const { session, read, send } = setup();
		await session.refresh();
		send.mockRejectedValueOnce(error);
		expect(await session.command('start', {})).toBe(false);
		expect(session.getState()).toMatchObject({ status: 'blocked', block: 'uncertain' });
		expect(session.getState().snapshot?.version).toBe(2);
		expect(await session.command('start', {})).toBe(false);
		expect(send).toHaveBeenCalledTimes(1);
		expect(read).toHaveBeenCalledTimes(1);
	});

	it('non considera aggiornata una lettura fallita o di altro contesto', async () => {
		const { session, read } = setup();
		await session.refresh();
		read.mockResolvedValueOnce({ ...snapshot(3), championship_id: 8 });
		expect(await session.refresh()).toBe(false);
		expect(session.getState()).toMatchObject({ status: 'blocked', block: 'read-failed' });
		expect(session.getState().snapshot?.championship_id).toBe(7);
	});

	it('rifiuta versioni obsolete anche se la risposta ha forma valida', async () => {
		const { session, send } = setup();
		await session.refresh();
		send.mockResolvedValueOnce(snapshot(1));
		expect(await session.command('start', {})).toBe(false);
		expect(session.getState().block).toBe('uncertain');
		expect(session.getState().snapshot?.version).toBe(2);
	});

	it.each([401, 403])('rimuove lo snapshot su HTTP %s', async (status) => {
		const { session, send } = setup();
		await session.refresh();
		send.mockRejectedValueOnce(new ApiError(status, 'Non autorizzato'));
		await session.command('start', {});
		expect(session.getState()).toMatchObject({
			status: 'blocked',
			block: 'authorization',
			snapshot: null
		});
	});

	it('scarta una lettura tardiva dopo cambio generazione autenticata', async () => {
		const { session, read, changeContext } = setup();
		const pending = deferred<unknown>();
		read.mockReturnValueOnce(pending.promise);
		const loading = session.refresh();
		changeContext('auth-2:judge:draft-1');
		pending.resolve(snapshot());
		expect(await loading).toBe(false);
		expect(session.getState()).toMatchObject({ status: 'disposed', snapshot: null });
	});

	it('scarta una scrittura tardiva senza fingere di annullare il server', async () => {
		const { session, send, changeContext } = setup();
		await session.refresh();
		const pending = deferred<unknown>();
		send.mockReturnValueOnce(pending.promise);
		const writing = session.command('start', {});
		changeContext(null);
		pending.resolve(snapshot(3));
		expect(await writing).toBe(false);
		expect(send).toHaveBeenCalledTimes(1);
		expect(session.getState().status).toBe('disposed');
	});

	it('dispose e definitivo anche quando arriva una risposta', async () => {
		const { session, read } = setup();
		const pending = deferred<unknown>();
		read.mockReturnValueOnce(pending.promise);
		const loading = session.refresh();
		session.dispose();
		pending.resolve(snapshot());
		expect(await loading).toBe(false);
		expect(await session.refresh()).toBe(false);
		expect(session.getState().snapshot).toBeNull();
	});

	it('distingue pronto intermedio, gara creata e annullamento', async () => {
		const { session, send } = setup();
		await session.refresh();
		send.mockResolvedValueOnce({ preparation: snapshot(3), race_id: null });
		expect(await session.command('ready', { pilot_id: 11, ready: true })).toBe(true);
		expect(session.getState().status).toBe('idle');
		send.mockResolvedValueOnce({ preparation: null, race_id: 9 });
		expect(await session.command('ready', { pilot_id: 11, ready: true })).toBe(true);
		expect(session.getState()).toMatchObject({
			status: 'finished',
			completion: 'race',
			raceId: 9,
			snapshot: null
		});
		expect(await session.command('start', {})).toBe(false);
		expect(await session.refresh()).toBe(false);
		const cancelled = setup();
		await cancelled.session.refresh();
		cancelled.send.mockResolvedValueOnce(undefined);
		expect(await cancelled.session.command('cancel', {})).toBe(true);
		expect(cancelled.session.getState()).toMatchObject({
			status: 'finished',
			completion: 'cancelled',
			raceId: null
		});
	});

	it('accetta gara gia disputata solo con esito terminale valido', async () => {
		const { session, send } = setup();
		await session.refresh();
		send.mockResolvedValueOnce({ preparation: null, race_id: 10 });
		expect(await session.command('already-disputed', {})).toBe(true);
		expect(session.getState().raceId).toBe(10);
	});
});
