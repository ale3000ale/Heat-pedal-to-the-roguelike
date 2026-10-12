// Servizio API per la revisione delle carte: una funzione per ogni rotta del backend.
import { api } from '$lib/api';
import type { CardMove, JudgePlay, PilotPlays, RaceReview } from '$lib/race-review-types';

// Costruisce la base dell'URL di una gara.
function raceBase(championshipId: number, raceId: number): string {
	return `/championships/${championshipId}/races/${raceId}`;
}

/** Apre la revisione o riprende la propria. Errore 409 se la tiene un altro utente. */
export function openReview(championshipId: number, raceId: number): Promise<RaceReview> {
	return api<RaceReview>(`${raceBase(championshipId, raceId)}/review`, { method: 'POST' });
}

/** Il revisore rinuncia: la gara torna "da rivedere". */
export function abandonReview(championshipId: number, raceId: number): Promise<RaceReview> {
	return api<RaceReview>(`${raceBase(championshipId, raceId)}/review`, { method: 'DELETE' });
}

/** Conferma la revisione e consuma le carte giocate. */
export function confirmReview(championshipId: number, raceId: number): Promise<RaceReview> {
	return api<RaceReview>(`${raceBase(championshipId, raceId)}/review/confirm`, {
		method: 'POST'
	});
}

/** Riepilogo delle carte giocate da tutti i piloti nella gara. */
export function fetchCardPlays(championshipId: number, raceId: number): Promise<PilotPlays[]> {
	return api<PilotPlays[]>(`${raceBase(championshipId, raceId)}/card-plays`);
}

/** Annulla una giocata attiva (solo il revisore, a revisione attiva). */
export function cancelPlay(
	championshipId: number,
	raceId: number,
	playId: number
): Promise<JudgePlay> {
	return api<JudgePlay>(`${raceBase(championshipId, raceId)}/card-plays/${playId}/cancel`, {
		method: 'POST'
	});
}

/** Bonus: una copia dalla pool all'inventario del pilota. */
export function grantBonus(
	championshipId: number,
	raceId: number,
	pilotId: number,
	cardName: string
): Promise<CardMove> {
	return api<CardMove>(`${raceBase(championshipId, raceId)}/card-bonus`, {
		method: 'POST',
		body: { pilot_id: pilotId, card_name: cardName }
	});
}

/** Rimozione: una copia dall'inventario del pilota alla pool sponsor. */
export function removeCard(
	championshipId: number,
	raceId: number,
	pilotId: number,
	cardName: string
): Promise<CardMove> {
	return api<CardMove>(`${raceBase(championshipId, raceId)}/card-removal`, {
		method: 'POST',
		body: { pilot_id: pilotId, card_name: cardName }
	});
}
