export const DOMAIN_EVENTS = [
	'championship.pilots_changed',
	'card.gifted',
	'card.gift_undone',
	'card.played',
	'card.play_undone',
	'cards.changed',
	'race.started',
	'race.review_changed',
	'race.results_changed',
	'standings.changed',
	'draft.changed'
] as const;

export type DomainEventType = (typeof DOMAIN_EVENTS)[number];
export type JsonValue =
	null | boolean | number | string | JsonValue[] | { [key: string]: JsonValue };
export type StreamEvent =
	| {
			type: DomainEventType;
			id: string;
			championshipId: number;
			pilotId: number | null;
			payload: Record<string, JsonValue>;
	  }
	| {
			type: 'resync';
			id: string | null;
			reason: 'initial' | 'cursor_unavailable' | 'invalid_event' | 'reconnected';
	  }
	| { type: 'auth.expired' };

export type ConnectionStatus =
	'stopped' | 'connecting' | 'open' | 'retrying' | 'unsupported' | 'expired';
export type EventFilter = { championshipId?: number; raceId?: number };
export type Listener<T> = (value: T) => void | Promise<void>;
