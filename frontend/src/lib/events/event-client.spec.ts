import { afterEach, describe, expect, it, vi } from 'vitest';
import { EventClient, type EventSourceLike } from './event-client';

class FakeSource extends EventTarget implements EventSourceLike {
	readyState = 0;
	close = vi.fn(() => {
		this.readyState = 2;
	});
	send(type: string, data = '{}', id = '') {
		this.dispatchEvent(new MessageEvent(type, { data, lastEventId: id }));
	}
}

const clients: EventClient[] = [];
function setup() {
	const sources: FakeSource[] = [];
	const factory = vi.fn(() => {
		const source = new FakeSource();
		sources.push(source);
		return source;
	});
	const client = new EventClient(factory);
	clients.push(client);
	return { client, sources, factory };
}

const body = JSON.stringify({ championship_id: 1, pilot_id: 2, payload: { race_id: 3 } });
afterEach(() => {
	for (const client of clients.splice(0)) client.disconnect();
	vi.useRealTimers();
	vi.restoreAllMocks();
});

describe('client SSE condiviso', () => {
	it('non connette nel costruttore; sostituisce sessione e protegge il nuovo cleanup', () => {
		const { client, sources, factory } = setup();
		expect(factory).not.toHaveBeenCalled();
		const firstStop = client.connect(1, vi.fn());
		const received = vi.fn();
		client.subscribe(received);
		const secondStop = client.connect(2, vi.fn());
		firstStop();
		sources[0].send('cards.changed', body, '1');
		sources[1].send('cards.changed', body, '2');
		expect(sources[0].close).toHaveBeenCalledOnce();
		expect(sources[1].close).not.toHaveBeenCalled();
		expect(received).toHaveBeenCalledOnce();
		expect(factory).toHaveBeenCalledWith('/api/events/stream');
		secondStop();
		expect(sources[1].close).toHaveBeenCalledOnce();
	});

	it('filtra campionato/gara, passa resync e disiscrive', () => {
		const { client, sources } = setup();
		client.connect(1, vi.fn());
		const own = vi.fn();
		const other = vi.fn();
		const stop = client.subscribe(own, { championshipId: 1, raceId: 3 });
		client.subscribe(other, { championshipId: 9 });
		sources[0].send('cards.changed', body, '1');
		expect(own).toHaveBeenCalledOnce();
		expect(other).not.toHaveBeenCalled();
		sources[0].send('resync', '{"reason":"initial"}', '1');
		expect(other).toHaveBeenCalledOnce();
		stop();
		sources[0].send('cards.changed', body, '2');
		expect(own).toHaveBeenCalledTimes(2);
	});

	it('non maschera un evento malformato e isola errori sincroni e asincroni', async () => {
		const log = vi.spyOn(console, 'error').mockImplementation(() => {});
		const { client, sources } = setup();
		client.connect(1, vi.fn());
		client.subscribe(() => {
			throw new Error('sync');
		});
		client.subscribe(async () => {
			throw new Error('async');
		});
		const received = vi.fn();
		client.subscribe(received);
		sources[0].send('cards.changed', '{', '1');
		await Promise.resolve();
		expect(received).toHaveBeenCalledWith({ type: 'resync', id: null, reason: 'invalid_event' });
		expect(log).toHaveBeenCalledTimes(2);
	});

	it('mantiene il retry nativo e riapre solo una sorgente chiusa', () => {
		vi.useFakeTimers();
		const { client, sources, factory } = setup();
		const status = vi.fn();
		client.subscribeStatus(status);
		client.connect(1, vi.fn());
		sources[0].send('open');
		sources[0].send('error');
		vi.advanceTimersByTime(3000);
		expect(factory).toHaveBeenCalledOnce();
		expect(status).toHaveBeenLastCalledWith('retrying');
		sources[0].readyState = 2;
		sources[0].send('error');
		vi.advanceTimersByTime(3000);
		expect(factory).toHaveBeenCalledTimes(2);
		client.disconnect();
		vi.advanceTimersByTime(6000);
		expect(factory).toHaveBeenCalledTimes(2);
	});

	it('auth.expired chiude prima del callback e non riconnette', () => {
		vi.useFakeTimers();
		const { client, sources, factory } = setup();
		const expired = vi.fn(() => {
			expect(sources[0].close).toHaveBeenCalledOnce();
		});
		const status = vi.fn();
		client.subscribeStatus(status);
		client.connect(1, expired);
		sources[0].send('auth.expired');
		vi.advanceTimersByTime(6000);
		expect(expired).toHaveBeenCalledOnce();
		expect(status).toHaveBeenLastCalledWith('expired');
		expect(factory).toHaveBeenCalledOnce();
	});

	it('gestisce assenza EventSource e valida userId', () => {
		const client = new EventClient(() => null);
		clients.push(client);
		const status = vi.fn();
		client.subscribeStatus(status);
		client.connect(1, vi.fn());
		expect(status).toHaveBeenLastCalledWith('unsupported');
		expect(() => client.connect(0, vi.fn())).toThrow(RangeError);
	});
});
