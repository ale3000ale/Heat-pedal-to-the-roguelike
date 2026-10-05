// Gara di un campionato, come appare nell'elenco. La data può non essere impostata.
export interface Race {
	id: number;
	number: number;
	date: string | null;
	participants: number;
}

// Risultato di un pilota in una gara. Chi non ha partecipato ha 0 punti.
export interface RaceResult {
	pilot_id: number;
	pilot_name: string;
	position: number | null;
	points: number;
}

// Gara con i risultati.
export interface RaceDetail extends Race {
	results: RaceResult[];
}

// Riga della classifica ufficiale. Nei campionati chiusi pilot_id può essere nullo.
export interface Standing {
	rank: number;
	pilot_id: number | null;
	pilot_name: string;
	points: number;
	races_played: number;
}
