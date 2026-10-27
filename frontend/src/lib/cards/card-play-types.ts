// Tipi delle carte sponsor giocate in gara, rispecchiano gli schemi del backend
// (`backend/app/schemas/cards/card_play.py` e `card_gift.py`). Le date arrivano come testo ISO.

// Stato di una giocata: `giocata` (attiva), `annullata` (restituita) o `consumata` (gara chiusa).
export type CardPlayStatus = 'giocata' | 'annullata' | 'consumata';

export type CardPlay = {
	id: number;
	card_name: string;
	card_path: string;
	status: CardPlayStatus;
	played_at: string;
};

// Carta sponsor dell'inventario con le copie ancora giocabili nella gara in corso.
export type AvailableCard = {
	name: string;
	path: string;
	copies_total: number;
	copies_available: number;
};

// Stato delle giocate di un pilota nella gara in corso.
// `in_review` indica che la gara è in revisione: non si può più giocare né annullare.
export type CardPlayState = {
	race_id: number;
	pilot_id: number;
	plays: CardPlay[];
	available: AvailableCard[];
	undo_remaining: number;
	in_review: boolean;
};

// Notifica "Hai ottenuto una carta sponsor" (tasto S del giudice o dell'admin).
export type CardGift = {
	id: number;
	race_id: number;
	card_name: string;
	card_path: string;
	created_at: string;
};

// Gruppo di copie uguali di una carta, mostrato con "x N".
export type CardGroup = {
	name: string;
	path: string;
	count: number;
};

// Intervallo (in secondi) con cui il giocatore controlla le nuove notifiche.
export type CardPollSetting = {
	seconds: number;
};
