import { api, ApiError } from './api';
import type { ChampionshipDetail, Pilot } from './types';
import type { Race, Standing } from './race-types';
import {
	acknowledgeGiftNotifications,
	fetchGiftNotifications,
	type PilotGiftNotification
} from './gift-notifications-api';
import { createGiftPopupController } from './gift-popup-controller';
import { startLiveRefresh, type LiveRefreshOptions } from './events/live-refresh.svelte';

export interface ChampionshipSnapshot {
	championship: ChampionshipDetail;
	standings: Standing[];
	races: Race[];
	myPilots: Pilot[];
	gifts: PilotGiftNotification[];
}

export interface ChampionshipLiveOptions {
	championshipId: number;
	intervalMs: number;
	onSnapshot: (snapshot: ChampionshipSnapshot) => void;
	onGifts: (visible: readonly PilotGiftNotification[]) => void;
	onError: (error: unknown) => void;
	onUnauthorized: () => void;
	client?: LiveRefreshOptions<ChampionshipSnapshot>['client'];
	fetch?: typeof fetch;
	load?: () => Promise<ChampionshipSnapshot>;
}

/**
 * Legge i dati della pagina e le notifiche dei soli piloti propri iscritti.
 * @param championshipId Campionato da leggere.
 * @param doFetch Fetch opzionale per test o integrazione.
 * @returns Snapshot completo pronto per apply; nessun effetto UI durante load.
 * @throws ApiError se una qualsiasi lettura fallisce; nessun risultato parziale.
 * Non e' una singola transazione SQL: sono piu' letture REST autorizzate.
 * Come prima, nei campionati chiusi non vengono aperte notifiche di regali.
 */
export async function fetchChampionshipSnapshot(
	championshipId: number,
	doFetch?: typeof fetch
): Promise<ChampionshipSnapshot> {
	const base = `/championships/${championshipId}`;
	const [championship, standings, races, myPilots] = await Promise.all([
		api<ChampionshipDetail>(base, { fetch: doFetch }),
		api<Standing[]>(`${base}/standings`, { fetch: doFetch }),
		api<Race[]>(`${base}/races`, { fetch: doFetch }),
		api<Pilot[]>('/pilots', { fetch: doFetch })
	]);
	const enrolled = new Set(championship.pilots.map((pilot) => pilot.id));
	const pilotIds = myPilots.filter((pilot) => enrolled.has(pilot.id)).map((pilot) => pilot.id);
	const gifts = championship.is_closed
		? []
		: await fetchGiftNotifications(championshipId, pilotIds, doFetch);
	return { championship, standings, races, myPilots, gifts };
}

/**
 * Collega snapshot, popup e coordinatore SSE condiviso per un contesto immutabile.
 * @param options Campionato, intervallo, callback e dipendenze opzionali per test.
 * @returns refresh, close con i soli ID resi e dispose al cambio campionato/utente.
 * @throws RangeError se l'intervallo non e' valido, come nel coordinatore condiviso.
 * Gli errori REST passano alle callback; 401 ferma tutto prima di onUnauthorized.
 * Non crea EventSource e non scrive in risposta a eventi SSE o annulli remoti.
 */
export function startChampionshipLive(options: ChampionshipLiveOptions) {
	let disposed = false;
	let live: { refresh: () => Promise<void>; dispose: () => void } | null = null;
	const popup = createGiftPopupController({
		acknowledge: (shown) =>
			acknowledgeGiftNotifications(options.championshipId, shown, options.fetch),
		onChange: options.onGifts,
		onError: handleError
	});

	function dispose(): void {
		if (disposed) return;
		disposed = true;
		popup.dispose();
		live?.dispose();
	}

	function expire(): void {
		if (disposed) return;
		dispose();
		options.onUnauthorized();
	}

	function handleError(error: unknown): void {
		if (disposed) return;
		if (error instanceof ApiError && error.status === 401) expire();
		else options.onError(error);
	}

	live = startLiveRefresh({
		intervalMs: options.intervalMs,
		filter: { championshipId: options.championshipId },
		client: options.client,
		load:
			options.load ??
			(() => fetchChampionshipSnapshot(options.championshipId, options.fetch)),
		apply: (snapshot) => {
			options.onSnapshot(snapshot);
			popup.update(snapshot.gifts);
		},
		onError: handleError,
		onUnauthorized: expire
	});

	/**
	 * Conferma una chiusura volontaria e invalida le letture iniziate prima dell'ack.
	 * @param shownIds Identificatori dell'ultima lista resa dal popup.
	 * @returns Attende conferma e rilettura accorpata, senza effetti dopo dispose.
	 */
	async function close(shownIds: readonly number[]): Promise<void> {
		if (disposed) return;
		await popup.close(shownIds);
		if (!disposed) await live?.refresh();
	}

	return {
		refresh: () => live?.refresh() ?? Promise.resolve(),
		close,
		dispose
	};
}
