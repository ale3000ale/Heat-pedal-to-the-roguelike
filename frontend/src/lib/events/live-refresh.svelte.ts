import { ApiError } from '$lib/api';
import { eventClient, type EventClient } from './event-client';
import type { DomainEventType, EventFilter } from './event-types';
import { createRefreshCoalescer, type RefreshOptions } from './refresh-coalescer';

export interface LiveRefreshOptions<T> extends RefreshOptions<T> {
	intervalMs: number;
	filter: EventFilter;
	types?: readonly DomainEventType[];
	onUnauthorized: () => void;
	client?: Pick<EventClient, 'subscribe' | 'subscribeStatus'>;
}

/**
 * Coordina una risorsa REST con SSE e polling solo quando lo stream non e' open.
 * @param options Lettura/applicazione, filtri, intervallo impostato e callback errori.
 * @returns refresh manuale e dispose da chiamare nello smontaggio/cambio contesto.
 * @throws RangeError per intervallo non intero, non positivo o oltre il limite timer.
 * Non apre stream, non scrive dati e non aggiorna direttamente auth o form locali.
 * onUnauthorized gestisce il 401 nel chiamante, dopo stop di timer e sottoscrizioni.
 */
export function startLiveRefresh<T>(options: LiveRefreshOptions<T>) {
	if (
		!Number.isSafeInteger(options.intervalMs) ||
		options.intervalMs < 1 ||
		options.intervalMs > 2147483647
	) {
		throw new RangeError('Intervallo non valido');
	}
	const client = options.client ?? eventClient;
	let disposed = false;
	let streamOpen = false;
	let timer: ReturnType<typeof setTimeout> | null = null;
	let unsubscribeEvents = () => {};
	let unsubscribeStatus = () => {};
	const refresh = createRefreshCoalescer<T>({
		load: options.load,
		apply: options.apply,
		onError: (error) => {
			if (error instanceof ApiError && error.status === 401) {
				dispose();
				options.onUnauthorized();
			} else {
				options.onError(error);
			}
		}
	});

	function clearTimer(): void {
		if (timer !== null) clearTimeout(timer);
		timer = null;
	}

	function schedule(): void {
		if (disposed || streamOpen || timer !== null) return;
		timer = setTimeout(() => {
			timer = null;
			if (disposed || streamOpen) return;
			void refresh.request().then(schedule);
		}, options.intervalMs);
	}

	function dispose(): void {
		if (disposed) return;
		disposed = true;
		clearTimer();
		refresh.dispose();
		unsubscribeEvents();
		unsubscribeStatus();
	}

	unsubscribeEvents = client.subscribe((event) => {
		if (disposed) return;
		if (event.type === 'auth.expired') {
			dispose();
			return;
		}
		if (event.type === 'resync' || !options.types || options.types.includes(event.type)) {
			void refresh.request();
		}
	}, options.filter);
	unsubscribeStatus = client.subscribeStatus((status) => {
		if (disposed) return;
		if (status === 'expired') {
			dispose();
			return;
		}
		streamOpen = status === 'open';
		if (streamOpen) clearTimer();
		else schedule();
	});
	if (disposed) {
		unsubscribeEvents();
		unsubscribeStatus();
	} else {
		void refresh.request().then(schedule);
	}
	return { refresh: refresh.request, dispose };
}
