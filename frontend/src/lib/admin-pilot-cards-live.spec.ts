import { describe, expect, it, vi } from 'vitest';
import { startAdminPilotCardsLive } from './admin-pilot-cards-live';
import {
	appendAdminCardDraftTransfer,
	createAdminCardDraftSession,
	resetAdminCardDraftSession,
	type AdminCardDraftSession
} from './admin-pilot-cards-session';
import type { AdminPilotCardsRead } from './admin-pilot-cards-types';
import type {
	ConnectionStatus,
	DomainEventType,
	Listener,
	StreamEvent
} from './events/event-types';

const path = 'cards/turbo.webp';
function snapshot(): AdminPilotCardsRead {
	const deck = (id: number) => ({
		available: true,
		id,
		version: 3,
		cards: [{ name: 'Turbo', path, copies: 2 }]
	});
	return {
		championship_id: 7,
		pilot: { pilot_id: 11, name: 'Anna', user_id: 5, username: 'mario' },
		read_only: false,
		blocked_reason: null,
		containers: {
			game_deck: deck(1),
			modification_inventory: deck(2),
			sponsor_inventory: deck(3),
			modification_pool: deck(4),
			sponsor_pool: deck(5)
		}
	};
}
function deferred<T>() {
	let resolve!: (value: T) => void;
	let reject!: (error: unknown) => void;
	const promise = new Promise<T>((yes, no) => {
		resolve = yes;
		reject = no;
	});
	return { promise, resolve, reject };
}
async function flush() {
	for (let i = 0; i < 30; i += 1) await Promise.resolve();
}
function harness() {
	const state: { session: AdminCardDraftSession | null; busy: boolean; current: boolean } = {
		session: null,
		busy: false,
		current: true
	};
	const reads: ReturnType<typeof deferred<AdminPilotCardsRead>>[] = [];
	let listener: Listener<StreamEvent> | undefined;
	const eventOff = vi.fn();
	const statusOff = vi.fn();
	const onError = vi.fn();
	const onExpired = vi.fn();
	const client = {
		subscribe: vi.fn((next: Listener<StreamEvent>) => {
			listener = next;
			return eventOff;
		}),
		subscribeStatus: vi.fn((next: Listener<ConnectionStatus>) => {
			void next('connecting');
			return statusOff;
		}),
		connect: vi.fn(),
		disconnect: vi.fn()
	};
	const applySession = vi.fn((next: AdminCardDraftSession) => {
		state.session = next;
		live.stateChanged();
	});
	const live: ReturnType<typeof startAdminPilotCardsLive> = startAdminPilotCardsLive({
		championshipId: 7,
		pilotId: 11,
		client,
		getSession: () => state.session,
		isRequestBusy: () => state.busy,
		isCurrent: () => state.current,
		applySession,
		onError,
		onExpired,
		load: () => {
			const read = deferred<AdminPilotCardsRead>();
			reads.push(read);
			return read.promise;
		}
	});
	return {
		state,
		reads,
		client,
		eventOff,
		statusOff,
		applySession,
		onError,
		onExpired,
		live,
		emit(type: DomainEventType) {
			if (listener) void listener({ type, id: '1', championshipId: 7, pilotId: null, payload: {} });
		},
		expire() {
			if (listener) void listener({ type: 'auth.expired' });
		}
	};
}

describe('integrazione live della sessione admin', () => {
	it('carica lo snapshot e usa solo il client condiviso', async () => {
		const h = harness();
		h.reads[0].resolve(snapshot());
		await flush();
		expect(h.state.session?.baseline.championship_id).toBe(7);
		expect(h.client.subscribe).toHaveBeenCalledWith(expect.any(Function), { championshipId: 7 });
		h.live.dispose();
		expect(h.client.connect).not.toHaveBeenCalled();
		expect(h.client.disconnect).not.toHaveBeenCalled();
	});

	it('blocca una bozza alla gara aperta, senza GET o scarto sul reset locale', async () => {
		const h = harness();
		h.reads[0].resolve(snapshot());
		await flush();
		h.state.session = appendAdminCardDraftTransfer(createAdminCardDraftSession(snapshot()), {
			source: 'game_deck',
			path
		});
		const original = h.state.session;
		h.emit('race.started');
		expect(h.state.session).not.toBe(original);
		expect(h.state.session?.transfers).toEqual(original.transfers);
		expect(h.state.session?.blockedReason).not.toBeNull();
		expect(h.reads).toHaveLength(1);
		h.state.session = resetAdminCardDraftSession(h.state.session!);
		h.live.stateChanged();
		await flush();
		expect(h.reads).toHaveLength(1);
		h.live.dispose();
	});

	it('rinvia il proprio evento durante PUT e accetta il successo prima della rilettura', async () => {
		const h = harness();
		h.reads[0].resolve(snapshot());
		await flush();
		h.state.session = appendAdminCardDraftTransfer(createAdminCardDraftSession(snapshot()), {
			source: 'game_deck',
			path
		});
		const original = h.state.session;
		h.state.busy = true;
		h.live.stateChanged();
		h.emit('cards.changed');
		expect(h.state.session).toBe(original);
		const saved = snapshot();
		saved.containers.game_deck.version = 4;
		h.live.acceptServerSession(createAdminCardDraftSession(saved));
		expect(h.state.session?.transfers).toEqual([]);
		expect(h.state.session?.baseline.containers.game_deck.version).toBe(4);
		expect(h.reads).toHaveLength(1);
		h.state.busy = false;
		h.live.stateChanged();
		expect(h.reads).toHaveLength(2);
		h.reads[1].resolve(saved);
		await flush();
		expect(h.state.session?.baseline.containers.game_deck.version).toBe(4);
		h.live.dispose();
	});

	it('rilegge un contesto di sola lettura quando cambia la gara', async () => {
		const h = harness();
		const closed = snapshot();
		closed.read_only = true;
		closed.blocked_reason = 'Gara aperta';
		h.reads[0].resolve(closed);
		await flush();
		h.emit('race.review_changed');
		expect(h.reads).toHaveLength(2);
		h.reads[1].resolve(snapshot());
		await flush();
		expect(h.state.session?.blockedReason).toBeNull();
		h.live.dispose();
	});

	it.each(['campionato', 'pilota'])(
		'rifiuta snapshot di altro %s senza applicarlo',
		async (context) => {
			const h = harness();
			const bad = snapshot();
			if (context === 'campionato') bad.championship_id = 8;
			else bad.pilot.pilot_id = 12;
			h.reads[0].resolve(bad);
			await flush();
			expect(h.state.session).toBeNull();
			expect(h.onError).toHaveBeenCalledTimes(1);
			expect(h.reads).toHaveLength(1);
			h.live.dispose();
		}
	);

	it('ignora risposte dopo cambio proprietario del contesto', async () => {
		const h = harness();
		h.state.current = false;
		h.reads[0].resolve(snapshot());
		await flush();
		expect(h.applySession).not.toHaveBeenCalled();
		expect(h.onError).not.toHaveBeenCalled();
		h.live.dispose();
	});

	it('scade e ignora una risposta tardiva senza chiudere lo stream condiviso', async () => {
		const h = harness();
		h.expire();
		h.reads[0].resolve(snapshot());
		await flush();
		expect(h.state.session).toBeNull();
		expect(h.onExpired).toHaveBeenCalledTimes(1);
		expect(h.eventOff).toHaveBeenCalledTimes(1);
		expect(h.statusOff).toHaveBeenCalledTimes(1);
		expect(h.client.disconnect).not.toHaveBeenCalled();
	});
});
