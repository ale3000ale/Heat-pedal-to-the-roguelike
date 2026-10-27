import { api } from '../api';
import { fetchUnseenGifts } from './card-play-api';
import type { CardGift } from './card-play-types';

export type PilotGiftNotification = {
	pilotId: number;
	gift: CardGift;
};

const SEEN_BATCH_SIZE = 100;

/**
 * Rifiuta identificatori che JavaScript non puo' rappresentare esattamente.
 * @param value Identificatore del campionato, pilota o regalo.
 * @returns Nessun valore quando l'identificatore e' un intero positivo sicuro.
 * @throws RangeError prima di inviare richieste con identificatori non validi.
 */
function requireId(value: number): void {
	if (!Number.isSafeInteger(value) || value < 1) {
		throw new RangeError('Identificatore non valido o non rappresentabile esattamente');
	}
}

/**
 * Legge uno snapshot completo, mantenendo il pilota assente dal DTO CardGift.
 * @param championshipId Campionato da leggere.
 * @param pilotIds Piloti propri; i duplicati sono letti una sola volta.
 * @param doFetch Fetch opzionale per i test.
 * @returns Notifiche associate al pilota della relativa richiesta REST.
 * @throws ApiError anche se fallisce un solo pilota: mai risultati parziali o [] fittizi.
 * @throws RangeError per identificatori non validi, prima di qualsiasi richiesta.
 */
export async function fetchGiftNotifications(
	championshipId: number,
	pilotIds: readonly number[],
	doFetch?: typeof fetch
): Promise<PilotGiftNotification[]> {
	requireId(championshipId);
	const uniqueIds = [...new Set(pilotIds)];
	uniqueIds.forEach(requireId);
	const lists = await Promise.all(
		uniqueIds.map(async (pilotId) => {
			const gifts = await fetchUnseenGifts(championshipId, pilotId, doFetch);
			return gifts.map((gift) => ({ pilotId, gift }));
		})
	);
	return lists.flat();
}

/**
 * Conferma esclusivamente le notifiche fornite dal chiamante come gia' mostrate.
 * @param championshipId Campionato delle notifiche.
 * @param displayed Snapshot delle notifiche mostrate, non tutta la coda non vista.
 * @param doFetch Fetch opzionale per i test.
 * @returns Si risolve dopo tutte le conferme, senza modificare lo snapshot o la UI.
 * @throws RangeError per ID non sicuri: tutti validati prima di qualsiasi invio.
 * @throws ApiError al primo batch fallito; i precedenti possono essere gia' confermati.
 * Il chiamante puo' ritentare lo stesso snapshot grazie all'idempotenza del backend.
 * La funzione non verifica il rendering e non deve essere chiamata per annulli remoti.
 */
export async function acknowledgeGiftNotifications(
	championshipId: number,
	displayed: readonly PilotGiftNotification[],
	doFetch?: typeof fetch
): Promise<void> {
	requireId(championshipId);
	const grouped = new Map<number, Set<number>>();
	for (const { pilotId, gift } of displayed) {
		requireId(pilotId);
		requireId(gift.id);
		const ids = grouped.get(pilotId) ?? new Set<number>();
		ids.add(gift.id);
		grouped.set(pilotId, ids);
	}
	for (const [pilotId, ids] of grouped) {
		const giftIds = [...ids];
		for (let offset = 0; offset < giftIds.length; offset += SEEN_BATCH_SIZE) {
			await api<void>(`/championships/${championshipId}/card-gifts/seen-selected`, {
				method: 'POST',
				body: {
					pilot_id: pilotId,
					gift_ids: giftIds.slice(offset, offset + SEEN_BATCH_SIZE)
				},
				fetch: doFetch
			});
		}
	}
}
