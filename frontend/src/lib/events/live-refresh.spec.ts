import { afterEach, describe, expect, it, vi } from 'vitest';
import { ApiError } from '$lib/api';
import type { ConnectionStatus, EventFilter, Listener, StreamEvent } from './event-types';
import { startLiveRefresh } from './live-refresh.svelte';

class FakeClient {
	status: ConnectionStatus = 'open';
	filter: EventFilter | null = null;
	events = new Set<Listener<StreamEvent>>();
	statuses = new Set<Listener<ConnectionStatus>>();

	subscribe(listener: Listener<StreamEvent>, filter: EventFilter = {}) {
		this.filter = filter;
		this.events.add(listener);
		return () => {
			this.events.delete(listener);
		};
	}

	subscribeStatus(listener: Listener<ConnectionStatus>) {
		this.statuses.add(listener);
		void listener(this.status);
		return () => {
			this.statuses.delete(listener);
		};
	}

	setStatus(status: ConnectionStatus) {
		this.status = status;
		for (const listener of this.statuses) void listener(status);
	}

	emit(event: StreamEvent) {
		for (const listener of this.events) void listener(event);
	}
}

const stops: (() => void)[] = [];
function setup() {
	const client = new FakeClient();
	const load = vi.fn(async () => 1);
	const apply = vi.fn();
	const onError = vi.fn();
	const onUnauthorized = vi.fn();
	const live = startLiveRefresh({
		client,
		load,
		apply,
		onError,
		onUnauthorized,
		intervalMs: 1000,
		filter: { championshipId: 1, raceId: 3 },
		types: ['cards.changed']
	});
	stops.push(live.dispose);
	return { client, load, apply, onError, onUnauthorized, live };
}

afterEach(() => {
	for (const stop of stops.splice(0)) stop();
	vi.useRealTimers();
});

describe('coordinatore SSE e fallback', () => {
	it('non fa polling con stream aperto; lo attiva e lo ferma sui cambi di stato', async () => {
		vi.useFakeTimers();
		const { client, load, live } = setup();
		await live.refresh();
		const initial = load.mock.calls.length;
		await vi.advanceTimersByTimeAsync(5000);
		expect(load).toHaveBeenCalledTimes(initial);
		client.setStatus('retrying');
		await vi.advanceTimersByTimeAsync(1000);
		expect(load).toHaveBeenCalledTimes(initial + 1);
		client.setStatus('open');
		await vi.advanceTimersByTimeAsync(5000);
		expect(load).toHaveBeenCalledTimes(initial + 1);
	});

	it('inoltra i filtri, ignora tipi non richiesti e rilegge per resync', async () => {
		const { client, load, live } = setup();
		await live.refresh();
		const initial = load.mock.calls.length;
		client.emit({
			type: 'standings.changed',
			id: '1',
			championshipId: 1,
			pilotId: null,
			payload: {}
		});
		expect(load).toHaveBeenCalledTimes(initial);
		client.emit({ type: 'resync', id: '2', reason: 'initial' });
		await Promise.resolve();
		expect(load).toHaveBeenCalledTimes(initial + 1);
		expect(client.filter).toEqual({ championshipId: 1, raceId: 3 });
	});

	it('401 interrompe lavoro e sottoscrizioni prima del callback', async () => {
		vi.useFakeTimers();
		const { client, load, onUnauthorized, onError, live } = setup();
		await live.refresh();
		load.mockRejectedValueOnce(new ApiError(401, 'Sessione scaduta'));
		await live.refresh();
		expect(onUnauthorized).toHaveBeenCalledOnce();
		expect(onError).not.toHaveBeenCalled();
		expect(client.events.size).toBe(0);
		expect(client.statuses.size).toBe(0);
		const count = load.mock.calls.length;
		await vi.advanceTimersByTimeAsync(5000);
		await live.refresh();
		expect(load).toHaveBeenCalledTimes(count);
	});

	it('auth.expired e dispose fermano le sottoscrizioni senza azioni REST di scrittura', async () => {
		const { client, load, onUnauthorized, live } = setup();
		await live.refresh();
		client.setStatus('expired');
		live.dispose();
		const count = load.mock.calls.length;
		client.emit({ type: 'resync', id: null, reason: 'reconnected' });
		await live.refresh();
		expect(load).toHaveBeenCalledTimes(count);
		expect(client.events.size).toBe(0);
		expect(client.statuses.size).toBe(0);
		expect(onUnauthorized).not.toHaveBeenCalled();
	});
});
