// Ruoli previsti dal backend: l'admin gestisce i campionati, il player i propri piloti.
export type Role = 'admin' | 'player';

// Utente come lo restituisce il backend (mai la password).
export interface User {
	id: number;
	username: string;
	role: Role;
}

// Team dell'utente.
export interface Team {
	id: number;
	name: string;
}

// Pilota come appare nell'elenco (senza i mazzi).
export interface Pilot {
	id: number;
	name: string;
	team_id: number | null;
	gold: number;
	sponsor: number;
	point: number;
}

// Una riga di mazzo: una carta con il numero di copie possedute.
export interface CardEntry {
	name: string;
	path: string;
	copies: number;
}

// Pilota con i suoi due mazzi (dettaglio).
export interface PilotDetail extends Pilot {
	inventory: CardEntry[];
	game_deck: CardEntry[];
}

// Campionato come appare nell'elenco.
export interface Championship {
	id: number;
	name: string;
	date: string;
	is_closed: boolean;
	pilots_count: number;
}

// Pilota iscritto a un campionato, visibile a tutti.
export interface Entrant {
	id: number;
	name: string;
	team_id: number | null;
	point: number;
}

// Campionato con i piloti iscritti.
export interface ChampionshipDetail extends Championship {
	pilots: Entrant[];
}
