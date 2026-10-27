import {
	fetchCardPoll,
	fetchUnseenGifts as fetchPilotGifts,
	markGiftsSeen as markPilotGiftsSeen
} from '$lib/cards/card-play-api';
import type { CardGift } from '$lib/cards/card-play-types';
import { CARD_POLL_DEFAULT, CARD_POLL_MAX, CARD_POLL_MIN } from '$lib/cards/card-poll-validation';

/**
 * Legge l'intervallo di controllo delle notifiche impostato dall'admin.
 * @returns Millisecondi tra due controlli. Se la lettura fallisce o il valore non rientra
 * nei limiti (da 1 a 10 secondi) si usa il valore predefinito di 5 secondi.
 */
export async function loadPollIntervalMs(): Promise<number> {
	try {
		const { seconds } = await fetchCardPoll();
		const valid = Number.isInteger(seconds) && seconds >= CARD_POLL_MIN && seconds <= CARD_POLL_MAX;
		return (valid ? seconds : CARD_POLL_DEFAULT) * 1000;
	} catch {
		return CARD_POLL_DEFAULT * 1000;
	}
}

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
			fetchPilotGifts(championshipId, pilotId).catch(() => [] as CardGift[])
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
	await Promise.all(pilotIds.map((pilotId) => markPilotGiftsSeen(championshipId, pilotId)));
}

/**
 * Esegue `check` subito e poi a intervalli regolari.
 * @param check Funzione da richiamare; gli errori vengono ignorati.
 * @param intervalMs Pausa tra due controlli (predefinita: 5 secondi).
 * @returns Funzione che ferma il controllo (da restituire da un $effect).
 */
export function startGiftPolling(
	check: () => Promise<void>,
	intervalMs: number = CARD_POLL_DEFAULT * 1000
): () => void {
	const run = () => {
		check().catch(() => {});
	};
	run();
	const timer = setInterval(run, intervalMs);
	return () => clearInterval(timer);
}
