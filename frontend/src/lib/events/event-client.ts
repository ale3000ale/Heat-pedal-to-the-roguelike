import { DOMAIN_EVENTS } from './event-types';
import type { ConnectionStatus, EventFilter, Listener, StreamEvent } from './event-types';
import { parseStreamEvent } from './event-validation';

export interface EventSourceLike {
	readonly readyState: number;
	addEventListener(type: string, listener: (event: Event) => void): void;
	removeEventListener(type: string, listener: (event: Event) => void): void;
	close(): void;
}

export type SourceFactory = (url: string) => EventSourceLike | null;
const STREAM_URL = '/api/events/stream';
const RETRY_MS = 3000;

function report(error: unknown): void {
	console.error('Errore nel sottoscrittore SSE', error);
}

function deliver<T>(listener: Listener<T>, value: T): void {
	try {
		void Promise.resolve(listener(value)).catch(report);
	} catch (error) {
		report(error);
	}
}

/** Connessione creata solo nel browser e solo dopo connect; nessun token in URL. */
function browserSource(url: string): EventSourceLike | null {
	return typeof EventSource === 'undefined' ? null : new EventSource(url);
}

export class EventClient {
	private source: EventSourceLike | null = null;
	private detach: (() => void) | null = null;
	private retry: ReturnType<typeof setTimeout> | null = null;
	private generation = 0;
	private status: ConnectionStatus = 'stopped';
	private events = new Set<{ listener: Listener<StreamEvent>; filter: EventFilter }>();
	private statuses = new Set<Listener<ConnectionStatus>>();

	constructor(private factory: SourceFactory = browserSource) {}

	/** Registra un listener; i controlli resync/auth passano sempre, anche con filtri. */
	subscribe(listener: Listener<StreamEvent>, filter: EventFilter = {}): () => void {
		const entry = { listener, filter: { ...filter } };
		this.events.add(entry);
		return () => {
			this.events.delete(entry);
		};
	}

	/** Stato del trasporto, non conferma che una rilettura REST sia completata. */
	subscribeStatus(listener: Listener<ConnectionStatus>): () => void {
		this.statuses.add(listener);
		deliver(listener, this.status);
		return () => {
			this.statuses.delete(listener);
		};
	}

	private setStatus(status: ConnectionStatus): void {
		if (status === this.status) return;
		this.status = status;
		for (const listener of [...this.statuses]) deliver(listener, status);
	}

	private publish(event: StreamEvent): void {
		const generation = this.generation;
		for (const entry of [...this.events]) {
			if (generation !== this.generation) return;
			if (!this.events.has(entry)) continue;
			if ('championshipId' in event) {
				if (
					entry.filter.championshipId !== undefined &&
					entry.filter.championshipId !== event.championshipId
				)
					continue;
				const raceId = event.payload.race_id;
				if (
					entry.filter.raceId !== undefined &&
					typeof raceId === 'number' &&
					entry.filter.raceId !== raceId
				)
					continue;
			}
			deliver(entry.listener, event);
		}
	}

	/** Chiude sorgente e timer; invalida anche callback gia' accodati dal browser. */
	disconnect(): void {
		this.generation += 1;
		if (this.retry !== null) clearTimeout(this.retry);
		this.retry = null;
		this.detach?.();
		this.detach = null;
		this.source = null;
		this.setStatus('stopped');
	}

	/**
	 * Avvia una sola sorgente per la sessione corrente, sostituendo quella precedente.
	 * @param userId Id positivo dell'utente autenticato; non viene inviato al server.
	 * @param onExpired Chiamato dopo aver chiuso lo stream per auth.expired.
	 * @returns Cleanup legato a questa generazione: non chiude una sessione successiva.
	 * @throws RangeError per userId non valido. Nessun dato o cursore viene persistito.
	 */
	connect(userId: number, onExpired: () => void): () => void {
		if (!Number.isSafeInteger(userId) || userId < 1) throw new RangeError('Utente non valido');
		this.disconnect();
		const generation = this.generation;
		const schedule = () => {
			if (generation !== this.generation || this.retry !== null) return;
			this.setStatus('retrying');
			this.retry = setTimeout(() => {
				this.retry = null;
				open();
			}, RETRY_MS);
		};
		const open = () => {
			if (generation !== this.generation) return;
			let source: EventSourceLike | null;
			try {
				source = this.factory(STREAM_URL);
			} catch {
				schedule();
				return;
			}
			if (!source) {
				this.setStatus('unsupported');
				return;
			}
			this.source = source;
			const listeners: [string, (event: Event) => void][] = [];
			const listen = (type: string, handler: (event: Event) => void) => {
				const listener = (event: Event) => {
					if (generation === this.generation && this.source === source) handler(event);
				};
				listeners.push([type, listener]);
				source.addEventListener(type, listener);
			};
			this.detach = () => {
				for (const [type, listener] of listeners) source.removeEventListener(type, listener);
				source.close();
			};
			let opened = false;
			listen('open', () => {
				this.setStatus('open');
				if (opened) this.publish({ type: 'resync', id: null, reason: 'reconnected' });
				opened = true;
			});
			listen('error', () => {
				this.setStatus('retrying');
				// CONNECTING: retry e Last-Event-ID restano gestiti da EventSource.
				if (source.readyState === 2) {
					this.detach?.();
					this.detach = null;
					this.source = null;
					schedule();
				}
			});
			for (const type of [...DOMAIN_EVENTS, 'resync', 'auth.expired', 'message']) {
				listen(type, (raw) => {
					const message = raw as MessageEvent<unknown>;
					const event = parseStreamEvent(type, message.data, message.lastEventId);
					if (!event) {
						this.publish({ type: 'resync', id: null, reason: 'invalid_event' });
						return;
					}
					if (event.type === 'auth.expired') {
						this.disconnect();
						this.setStatus('expired');
						this.publish(event);
						deliver(onExpired, undefined);
						return;
					}
					this.publish(event);
				});
			}
		};
		this.setStatus('connecting');
		open();
		return () => {
			if (generation === this.generation) this.disconnect();
		};
	}
}

// Il costruttore non usa API browser; la connessione parte dall'effetto del layout.
export const eventClient = new EventClient();
