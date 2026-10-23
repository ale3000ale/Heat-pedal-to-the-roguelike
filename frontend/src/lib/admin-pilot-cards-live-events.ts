import { eventClient, type EventClient } from './events/event-client';
import type { ConnectionStatus, DomainEventType } from './events/event-types';

export type AdminCardInvalidationReason = 'cards' | 'race' | 'access' | 'resync';
export interface AdminPilotCardsLiveOptions {
	championshipId: number;
	onInvalidate: (reason: AdminCardInvalidationReason) => void;
	onExpired: () => void;
	onStatus?: (status: ConnectionStatus) => void;
	client?: Pick<EventClient, 'subscribe' | 'subscribeStatus'>;
}

const invalidations: Partial<Record<DomainEventType, AdminCardInvalidationReason>> = {
	'cards.changed': 'cards',
	'card.gifted': 'cards',
	'card.gift_undone': 'cards',
	'card.played': 'cards',
	'card.play_undone': 'cards',
	'championship.pilots_changed': 'access',
	'race.started': 'race',
	'race.review_changed': 'race',
	'race.results_changed': 'race'
};

/**
 * Sottoscrive il client condiviso: segnali soltanto, senza aprire stream o fare REST.
 * @param options Campionato immutabile, callback e client opzionale per test.
 * @returns Cleanup idempotente dei soli listener registrati da questa funzione.
 * @throws RangeError per ID invalido; propaga errori di registrazione dopo cleanup.
 * Non passa payload alle callback, non modifica bozze e non autorizza scritture.
 * Il consumatore deve preservare la bozza e accorpare le eventuali riletture REST.
 */
export function subscribeAdminPilotCardsLive(options: AdminPilotCardsLiveOptions): () => void {
	if (!Number.isSafeInteger(options.championshipId) || options.championshipId <= 0) {
		throw new RangeError('ID campionato non valido');
	}
	const client = options.client ?? eventClient;
	const cleanups: (() => void)[] = [];
	let disposed = false;
	let lastStatus: ConnectionStatus | undefined;

	function register(stop: () => void): void {
		if (disposed) stop();
		else cleanups.push(stop);
	}
	function dispose(): void {
		if (disposed) return;
		disposed = true;
		for (const stop of cleanups.splice(0)) stop();
	}
	function expire(): void {
		dispose();
		options.onExpired();
	}

	try {
		register(
			client.subscribe(
				(event) => {
					if (disposed) return;
					if (event.type === 'auth.expired') {
						expire();
						return;
					}
					if (event.type === 'resync') {
						options.onInvalidate('resync');
						return;
					}
					if (event.championshipId !== options.championshipId) return;
					if (Object.hasOwn(invalidations, event.type)) {
						const reason = invalidations[event.type];
						if (reason) options.onInvalidate(reason);
					}
				},
				{ championshipId: options.championshipId }
			)
		);
		if (!disposed) {
			register(
				client.subscribeStatus((status) => {
					if (disposed || status === lastStatus) return;
					lastStatus = status;
					options.onStatus?.(status);
					if (disposed) return;
					if (status === 'expired') {
						expire();
						return;
					}
					if (status === 'open') options.onInvalidate('resync');
				})
			);
		}
	} catch (cause) {
		dispose();
		throw cause;
	}
	return dispose;
}
