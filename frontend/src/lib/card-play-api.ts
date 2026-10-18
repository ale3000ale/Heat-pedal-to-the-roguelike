import { api } from './api';
import type { CardGift, CardPlayState, CardPollSetting } from './card-play-types';

// Servizio API delle carte sponsor in gara. Ogni funzione lancia `ApiError` se il backend
// risponde con un errore (404, 403, 409 ...): le pagine ne mostrano il messaggio.

type Fetch = typeof fetch;

// Legge lo stato delle giocate di un pilota nella gara in corso.
export function fetchCardPlayState(
	championshipId: number,
	pilotId: number,
	doFetch?: Fetch
): Promise<CardPlayState> {
	return api<CardPlayState>(`/championships/${championshipId}/card-plays?pilot_id=${pilotId}`, {
		fetch: doFetch
	});
}

// Gioca una carta sponsor e restituisce lo stato aggiornato (riletto dal server,
// così non si dipende dal corpo della risposta di POST).
export async function playCard(
	championshipId: number,
	pilotId: number,
	cardName: string,
	doFetch?: Fetch
): Promise<CardPlayState> {
	await api<unknown>(`/championships/${championshipId}/card-plays`, {
		method: 'POST',
		body: { pilot_id: pilotId, card_name: cardName },
		fetch: doFetch
	});
	return fetchCardPlayState(championshipId, pilotId, doFetch);
}

// Annulla l'ultima carta giocata (massimo 5 annullamenti consecutivi) e restituisce
// lo stato aggiornato.
export async function undoCard(
	championshipId: number,
	pilotId: number,
	doFetch?: Fetch
): Promise<CardPlayState> {
	await api<unknown>(`/championships/${championshipId}/card-plays/undo`, {
		method: 'POST',
		body: { pilot_id: pilotId },
		fetch: doFetch
	});
	return fetchCardPlayState(championshipId, pilotId, doFetch);
}

// Giudice o admin: tasto S, assegna una carta sponsor casuale al pilota.
export function giveRandomCard(
	championshipId: number,
	pilotId: number,
	doFetch?: Fetch
): Promise<CardGift> {
	return api<CardGift>(`/championships/${championshipId}/card-gifts`, {
		method: 'POST',
		body: { pilot_id: pilotId },
		fetch: doFetch
	});
}

// Giocatore: notifiche di carta ottenuta non ancora viste dal pilota.
export function fetchUnseenGifts(
	championshipId: number,
	pilotId: number,
	doFetch?: Fetch
): Promise<CardGift[]> {
	return api<CardGift[]>(`/championships/${championshipId}/card-gifts?pilot_id=${pilotId}`, {
		fetch: doFetch
	});
}

// Giocatore: segna come viste le notifiche del pilota (risposta 204, senza corpo).
export function markGiftsSeen(
	championshipId: number,
	pilotId: number,
	doFetch?: Fetch
): Promise<void> {
	return api<void>(`/championships/${championshipId}/card-gifts/seen`, {
		method: 'POST',
		body: { pilot_id: pilotId },
		fetch: doFetch
	});
}

// Intervallo di controllo delle notifiche, leggibile da ogni utente collegato.
export function fetchCardPoll(doFetch?: Fetch): Promise<CardPollSetting> {
	return api<CardPollSetting>('/admin/card-poll', { fetch: doFetch });
}

// Solo admin: cambia l'intervallo (da 1 a 10 secondi).
export function saveCardPoll(seconds: number, doFetch?: Fetch): Promise<CardPollSetting> {
	return api<CardPollSetting>('/admin/card-poll', {
		method: 'PUT',
		body: { seconds },
		fetch: doFetch
	});
}
