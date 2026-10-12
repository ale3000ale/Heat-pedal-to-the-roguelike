// Tipi delle carte sponsor giocate e delle carte ottenute con il tasto S.
// Rispecchiano gli schemi del backend (card_play.py e card_gift.py).

// Stato di una giocata: solo 'giocata' conta per le copie disponibili.
export type CardPlayStatus = 'giocata' | 'annullata' | 'consumata';

// Una giocata registrata nella gara in corso.
export interface CardPlay {
	id: number;
	card_name: string;
	card_path: string;
	status: CardPlayStatus;
	played_at: string;
}

// Carta dell'inventario sponsor con le copie ancora giocabili.
export interface AvailableCard {
	name: string;
	path: string;
	copies_total: number;
	copies_available: number;
}

// Stato delle giocate di un pilota nella gara in corso.
export interface CardPlayState {
	race_id: number;
	pilot_id: number;
	plays: CardPlay[];
	available: AvailableCard[];
	undo_remaining: number;
	in_review: boolean;
}

// Carta ottenuta con il tasto S (anche come notifica).
export interface CardGift {
	id: number;
	race_id: number;
	card_name: string;
	card_path: string;
	created_at: string;
}
