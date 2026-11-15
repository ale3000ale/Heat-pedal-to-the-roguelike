import { describe, expect, it, vi } from 'vitest';
import { EventClient, type EventSourceLike } from './events/event-client';
import { parseStreamEvent } from './events/event-validation';

const signal = { championship_id: 7, pilot_id: null, payload: { preparation_id: 1 } };

describe('contratto draft.changed', () => {
	it('accetta il solo identificativo della preparazione con cursore esatto', () => {
		expect(
			parseStreamEvent('draft.changed', JSON.stringify(signal), '9223372036854775807')
		).toEqual({
			type: 'draft.changed',
			id: '9223372036854775807',
			championshipId: 7,
			pilotId: null,
			payload: { preparation_id: 1 }
		});
	});

	it.each([0, -1, 1.5, '1', null])('rifiuta preparation_id %s', (preparation_id) => {
		expect(
			parseStreamEvent(
				'draft.changed',
				JSON.stringify({ ...signal, payload: { preparation_id } }),
				'1'
			)
		).toBeNull();
	});

	it('rifiuta dettagli privati, ID mancante e riferimenti a piloti', () => {
		for (const payload of [{}, { preparation_id: 1, cards: [] }, { race_id: 2 }]) {
			expect(
				parseStreamEvent('draft.changed', JSON.stringify({ ...signal, payload }), '1')
			).toBeNull();
		}
		expect(
			parseStreamEvent('draft.changed', JSON.stringify({ ...signal, pilot_id: 11 }), '1')
		).toBeNull();
	});

	it('usa il client condiviso e trasforma un segnale malformato in resync', () => {
		class Source extends EventTarget implements EventSourceLike {
			readyState = 0;
			close = vi.fn();
		}
		const source = new Source();
		const factory = vi.fn(() => source);
		const client = new EventClient(factory);
		const received = vi.fn();
		client.subscribe(received);
		client.connect(9, vi.fn());
		try {
			source.dispatchEvent(
				new MessageEvent('draft.changed', { data: JSON.stringify(signal), lastEventId: '1' })
			);
			expect(received).toHaveBeenLastCalledWith({
				type: 'draft.changed',
				id: '1',
				championshipId: 7,
				pilotId: null,
				payload: { preparation_id: 1 }
			});
			source.dispatchEvent(new MessageEvent('draft.changed', { data: '{}', lastEventId: '2' }));
			expect(received).toHaveBeenLastCalledWith({
				type: 'resync',
				id: null,
				reason: 'invalid_event'
			});
			expect(factory).toHaveBeenCalledTimes(1);
		} finally {
			client.disconnect();
		}
	});
});
