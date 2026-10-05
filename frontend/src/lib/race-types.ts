// Gara di un campionato, come appare nell'elenco. La data può non essere impostata.
export interface Race {
	id: number;
	number: number;
	date: string | null;
	participants: number;
}

// Risultato di un pilota in una gara. Chi non ha partecipato ha 0 punti e 0 sponsor.
export interface RaceResult {
	pilot_id: number;
	pilot_name: string;
	position: number | null;
	points: number;
	sponsor_points: number;
}

// Gara con i risultati.
export interface RaceDetail extends Race {
	results: RaceResult[];
}

// Riga inviata al backend: l'ordine dell'elenco è l'ordine di arrivo.
export interface RaceResultInput {
	pilot_id: number;
	sponsor_points: number;
}

// Riga della classifica ufficiale. Nei campionati chiusi pilot_id può essere nullo.
export interface Standing {
	rank: number;
	pilot_id: number | null;
	pilot_name: string;
	points: number;
	races_played: number;
}

// Utente nell'elenco dell'admin.
export interface AdminUser {
	id: number;
	username: string;
	role: 'admin' | 'judge' | 'player';
}
