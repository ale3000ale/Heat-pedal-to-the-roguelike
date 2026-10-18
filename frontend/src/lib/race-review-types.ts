// Tipi della revisione delle carte, allineati agli schemi Pydantic del backend
// (backend/app/schemas/race_review.py e card_judge.py).

// Stato della revisione di una gara.
export interface RaceReview {
	race_id: number;
	in_review: boolean;
	review_started_at: string | null;
	reviewer_user_id: number | null;
	review_expires_at: string | null;
	review_closed_at: string | null;
}

// Una carta giocata da un pilota, come la vede il revisore.
export interface JudgePlay {
	id: number;
	card_name: string;
	card_path: string;
	status: string;
	played_at: string;
}

// Le carte giocate da un pilota nella gara.
export interface PilotPlays {
	pilot_id: number;
	pilot_name: string;
	plays: JudgePlay[];
}

// Risposta di bonus e rimozione: la carta mossa e il pilota coinvolto.
export interface CardMove {
	pilot_id: number;
	card_name: string;
	card_path: string;
}
