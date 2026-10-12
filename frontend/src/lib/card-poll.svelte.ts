import { api } from '$lib/api';
import type { CardGift } from '$lib/card-play-types';

// Intervallo fisso del controllo delle notifiche (l'impostazione configurabile arriva dopo).
export const GIFT_POLL_INTERVAL_MS = 15000;

/**
 * Legge le carte ottenute e non ancora viste dei piloti indicati.
 * @param championshipId Campionato da controllare.
 * @param pilotIds Piloti del giocatore iscritti al campionato.
 * @returns Le notifiche di tutti i piloti. Un errore su un pilota viene ignorato:
 * il controllo periodico non deve disturbare l'utente.
 */
export async function fetchUnseenGifts(
	championshipId: number,
	pilotIds: number[]
): Promise<CardGift[]> {
	const lists = await Promise.all(
		pilotIds.map((pilotId) =>
			api<CardGift[]>(`/championships/${championshipId}/card-gifts?pilot_id=${pilotId}`).catch(
				() => [] as CardGift[]
			)
		)
	);
	return lists.flat();
}

/**
 * Segna come viste le notifiche dei piloti indicati.
 * @param championshipId Campionato delle notifiche.
 * @param pilotIds Piloti di cui azzerare le notifiche.
 * @throws ApiError se il backend rifiuta la richiesta.
 */
export async function markGiftsSeen(championshipId: number, pilotIds: number[]): Promise<void> {
	await Promise.all(
		pilotIds.map((pilotId) =>
			api(`/championships/${championshipId}/card-gifts/seen`, {
				method: 'POST',
				body: { pilot_id: pilotId }
			})
		)
	);
}

/**
 * Esegue `check` subito e poi a intervalli regolari.
 * @param check Funzione da richiamare; gli errori vengono ignorati.
 * @param intervalMs Pausa tra due controlli.
 * @returns Funzione che ferma il controllo (da restituire da un $effect).
 */
export function startGiftPolling(
	check: () => Promise<void>,
	intervalMs: number = GIFT_POLL_INTERVAL_MS
): () => void {
	const run = () => {
		check().catch(() => {});
	};
	run();
	const timer = setInterval(run, intervalMs);
	return () => clearInterval(timer);
}
