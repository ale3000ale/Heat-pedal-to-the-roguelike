import { describe, expect, it, vi } from 'vitest';
import {
	subscribeAdminPilotCardsLive,
	type AdminCardInvalidationReason
} from './admin-pilot-cards-live-events';
import type {
	ConnectionStatus,
	DomainEventType,
	Listener,
	StreamEvent
} from './events/event-types';

function event(type: DomainEventType, championshipId = 7): StreamEvent {
	return {
		type,
		id: 'event-1',
		championshipId,
		pilotId: null,
		payload: { private_value: 'non inoltrare' }
	};
}

function harness(initial: ConnectionStatus = 'open') {
	const events = new Set<Listener<StreamEvent>>();
	const statuses = new Set<Listener<ConnectionStatus>>();
	let lastEvent: Listener<StreamEvent> | undefined;
	let lastStatus: Listener<ConnectionStatus> | undefined;
	const eventOff = vi.fn();
	const statusOff = vi.fn();
	const client = {
		subscribe: vi.fn((listener: Listener<StreamEvent>) => {
			lastEvent = listener;
			events.add(listener);
			return () => {
				events.delete(listener);
				eventOff();
			};
		}),
		subscribeStatus: vi.fn((listener: Listener<ConnectionStatus>) => {
			lastStatus = listener;
			statuses.add(listener);
			void listener(initial);
			return () => {
				statuses.delete(listener);
				statusOff();
			};
		}),
		connect: vi.fn(),
		disconnect: vi.fn()
	};
	return {
		client,
		eventOff,
		statusOff,
		emit(value: StreamEvent) {
			for (const listener of [...events]) void listener(value);
		},
		status(value: ConnectionStatus) {
			for (const listener of [...statuses]) void listener(value);
		},
		lateEvent(value: StreamEvent) {
			if (lastEvent) void lastEvent(value);
		},
		lateStatus(value: ConnectionStatus) {
			if (lastStatus) void lastStatus(value);
		}
	};
}

function attach(initial: ConnectionStatus = 'open') {
	const h = harness(initial);
	const onInvalidate = vi.fn();
	const onExpired = vi.fn();
	const onStatus = vi.fn();
	const dispose = subscribeAdminPilotCardsLive({
		championshipId: 7,
		client: h.client,
		onInvalidate,
		onExpired,
		onStatus
	});
	return { ...h, onInvalidate, onExpired, onStatus, dispose };
}

const cases: [DomainEventType, AdminCardInvalidationReason][] = [
	['cards.changed', 'cards'],
	['card.gifted', 'cards'],
	['card.gift_undone', 'cards'],
	['card.played', 'cards'],
	['card.play_undone', 'cards'],
	['championship.pilots_changed', 'access'],
	['race.started', 'race'],
	['race.review_changed', 'race'],
	['race.results_changed', 'race']
];

describe('sottoscrizione live admin al client SSE condiviso', () => {
	it('registra solo listener filtrati, senza connettere o disconnettere lo stream', () => {
		const h = attach();
		expect(h.client.subscribe).toHaveBeenCalledWith(expect.any(Function), { championshipId: 7 });
		expect(h.onStatus).toHaveBeenCalledWith('open');
		expect(h.onInvalidate).toHaveBeenCalledWith('resync');
		h.dispose();
		expect(h.client.connect).not.toHaveBeenCalled();
		expect(h.client.disconnect).not.toHaveBeenCalled();
	});

	it.each(cases)('classifica %s senza inoltrare payload o carte', (type, reason) => {
		const h = attach();
		h.onInvalidate.mockClear();
		h.emit(event(type));
		expect(h.onInvalidate).toHaveBeenCalledExactlyOnceWith(reason);
		h.dispose();
	});

	it('ricontrolla il campionato anche se il client finto non applica il filtro', () => {
		const h = attach();
		h.onInvalidate.mockClear();
		h.emit(event('cards.changed', 8));
		expect(h.onInvalidate).not.toHaveBeenCalled();
		h.dispose();
	});

	it('non invalida le carte per il solo aggiornamento della classifica', () => {
		const h = attach();
		h.onInvalidate.mockClear();
		h.emit(event('standings.changed'));
		expect(h.onInvalidate).not.toHaveBeenCalled();
		h.dispose();
	});

	it.each(['initial', 'cursor_unavailable', 'invalid_event', 'reconnected'] as const)(
		'propaga resync %s senza dati di dominio',
		(reason) => {
			const h = attach();
			h.onInvalidate.mockClear();
			h.emit({ type: 'resync', id: null, reason });
			expect(h.onInvalidate).toHaveBeenCalledExactlyOnceWith('resync');
			h.dispose();
		}
	);

	it('segnala lo stato del trasporto senza fingere una lettura REST', () => {
		const h = attach();
		h.onInvalidate.mockClear();
		h.status('retrying');
		h.status('unsupported');
		h.status('stopped');
		expect(h.onInvalidate).not.toHaveBeenCalled();
		expect(h.onStatus.mock.calls.map(([value]) => value)).toEqual([
			'open',
			'retrying',
			'unsupported',
			'stopped'
		]);
		h.dispose();
	});

	it('invalida alla riconnessione e non duplica lo stesso stato open', () => {
		const h = attach();
		h.onInvalidate.mockClear();
		h.status('retrying');
		h.status('open');
		h.status('open');
		expect(h.onInvalidate).toHaveBeenCalledExactlyOnceWith('resync');
		h.dispose();
	});

	it.each(['event', 'status'])(
		'scade una sola volta tramite %s e rimuove i propri listener',
		(mode) => {
			const h = attach();
			if (mode === 'event') h.emit({ type: 'auth.expired' });
			else h.status('expired');
			h.lateEvent({ type: 'auth.expired' });
			h.lateStatus('expired');
			h.dispose();
			expect(h.onExpired).toHaveBeenCalledTimes(1);
			expect(h.eventOff).toHaveBeenCalledTimes(1);
			expect(h.statusOff).toHaveBeenCalledTimes(1);
			expect(h.client.disconnect).not.toHaveBeenCalled();
		}
	);

	it('ignora callback tardive e rende il cleanup idempotente', () => {
		const h = attach();
		h.onInvalidate.mockClear();
		h.dispose();
		h.dispose();
		h.lateEvent(event('race.started'));
		h.lateStatus('open');
		expect(h.onInvalidate).not.toHaveBeenCalled();
		expect(h.eventOff).toHaveBeenCalledTimes(1);
		expect(h.statusOff).toHaveBeenCalledTimes(1);
	});

	it.each([0, -1, 1.5, NaN, Infinity, Number.MAX_SAFE_INTEGER + 1])(
		'rifiuta ID %s prima di sottoscrivere',
		(championshipId) => {
			const h = harness();
			expect(() => {
				subscribeAdminPilotCardsLive({
					championshipId,
					client: h.client,
					onInvalidate: vi.fn(),
					onExpired: vi.fn()
				});
			}).toThrow(RangeError);
			expect(h.client.subscribe).not.toHaveBeenCalled();
			expect(h.client.subscribeStatus).not.toHaveBeenCalled();
		}
	);

	it('gestisce expired sincrono durante la registrazione senza lasciare listener', () => {
		const h = attach('expired');
		expect(h.onExpired).toHaveBeenCalledTimes(1);
		expect(h.eventOff).toHaveBeenCalledTimes(1);
		expect(h.statusOff).toHaveBeenCalledTimes(1);
		h.dispose();
		expect(h.statusOff).toHaveBeenCalledTimes(1);
	});

	it('ripulisce la prima sottoscrizione se la seconda registrazione fallisce', () => {
		const h = harness();
		h.client.subscribeStatus.mockImplementationOnce(() => {
			throw new Error('Registrazione fallita');
		});
		expect(() => {
			subscribeAdminPilotCardsLive({
				championshipId: 7,
				client: h.client,
				onInvalidate: vi.fn(),
				onExpired: vi.fn()
			});
		}).toThrow('Registrazione fallita');
		expect(h.eventOff).toHaveBeenCalledTimes(1);
	});

	it('non rimuove listener appartenenti ad altri componenti', () => {
		const h = attach();
		const other = vi.fn();
		const stopOther = h.client.subscribe(other);
		h.onInvalidate.mockClear();
		h.dispose();
		h.emit(event('cards.changed'));
		expect(other).toHaveBeenCalledTimes(1);
		expect(h.onInvalidate).not.toHaveBeenCalled();
		stopOther();
	});
});
