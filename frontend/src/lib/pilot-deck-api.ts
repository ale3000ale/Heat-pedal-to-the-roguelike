import { api } from './api';
import type { CardEntry, PilotDetail } from './types';

// Lettura del mazzo da gioco di un pilota, per il riepilogo con immagini nella sua
// sezione delle carte sponsor. Lancia `ApiError` se il backend risponde con un errore
// (404, 403 ...): la pagina ne mostra il messaggio.
type Fetch = typeof fetch;

// Legge il mazzo da gioco in uso del pilota (campo `game_deck` del dettaglio).
// Parametri: pilotId, l'id del pilota; doFetch, iniettabile per i test.
// Ritorna: le carte del mazzo con nome, percorso e copie.
export async function fetchPilotGameDeck(pilotId: number, doFetch?: Fetch): Promise<CardEntry[]> {
	const detail = await api<PilotDetail>(`/pilots/${pilotId}`, { fetch: doFetch });
	return detail.game_deck;
}
