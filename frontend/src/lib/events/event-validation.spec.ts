import { describe, expect, it } from 'vitest';
import { DOMAIN_EVENTS } from './event-types';
import { parseStreamEvent } from './event-validation';

const body = { championship_id: 1, pilot_id: 2, payload: { race_id: 3 } };

describe('protocollo SSE', () => {
	it.each(DOMAIN_EVENTS)('accetta %s con cursore int64 esatto', (type) => {
		const value =
			type === 'championship.pilots_changed'
				? { championship_id: 1, pilot_id: null, payload: {} }
				: body;
		const event = parseStreamEvent(type, JSON.stringify(value), '9223372036854775807');
		expect(event).toMatchObject({
			type,
			id: '9223372036854775807',
			championshipId: 1,
			pilotId: value.pilot_id
		});
	});

	it('accetta resync iniziale con registro vuoto e auth.expired senza id', () => {
		expect(parseStreamEvent('resync', '{"reason":"initial"}', '0')).toEqual({
			type: 'resync',
			id: '0',
			reason: 'initial'
		});
		expect(parseStreamEvent('auth.expired', '{}', '')).toEqual({ type: 'auth.expired' });
		expect(parseStreamEvent('resync', '{"reason":"cursor_unavailable"}', '4')).not.toBeNull();
	});

	it.each(['', '-1', '1.5', '9223372036854775808', '01'])('rifiuta il cursore %s', (id) => {
		expect(parseStreamEvent('cards.changed', JSON.stringify(body), id)).toBeNull();
	});

	it('rifiuta JSON, tipi e riferimenti non validi', () => {
		expect(parseStreamEvent('cards.changed', '{', '1')).toBeNull();
		expect(parseStreamEvent('sconosciuto', JSON.stringify(body), '1')).toBeNull();
		expect(
			parseStreamEvent('cards.changed', JSON.stringify({ ...body, championship_id: -1 }), '1')
		).toBeNull();
		expect(
			parseStreamEvent('cards.changed', JSON.stringify({ ...body, pilot_id: '2' }), '1')
		).toBeNull();
		expect(
			parseStreamEvent('cards.changed', JSON.stringify({ ...body, payload: [] }), '1')
		).toBeNull();
		expect(
			parseStreamEvent(
				'cards.changed',
				'{"championship_id":1,"pilot_id":null,"payload":{"n":1e400}}',
				'1'
			)
		).toBeNull();
		expect(parseStreamEvent('resync', '{"reason":"altro"}', '1')).toBeNull();
		expect(parseStreamEvent('auth.expired', '{"card":"privata"}', '')).toBeNull();
	});
});

it('rifiuta dettagli pilota e payload sul segnale iscrizioni', () => {
	expect(parseStreamEvent('championship.pilots_changed', JSON.stringify(body), '1')).toBeNull();
	expect(
		parseStreamEvent(
			'championship.pilots_changed',
			JSON.stringify({ championship_id: 1, pilot_id: null, payload: { cards: ['privata'] } }),
			'1'
		)
	).toBeNull();
	expect(
		parseStreamEvent(
			'championship.pilots_changed',
			JSON.stringify({ championship_id: 1, pilot_id: 2, payload: {} }),
			'1'
		)
	).toBeNull();
});
