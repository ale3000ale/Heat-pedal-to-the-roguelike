// Ruoli previsti dal backend: l'admin gestisce tutto, il giudice chiude le gare,
// il player gestisce i propri piloti.
export type Role = 'admin' | 'judge' | 'player';

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

// Riferimento a un campionato (id e nome).
export interface ChampionshipRef {
	id: number;
	name: string;
}

// Pilota come appare nell'elenco (senza i mazzi), con il campionato attivo se iscritto.
export interface Pilot {
	id: number;
	name: string;
	team_id: number | null;
	gold: number;
	sponsor: number;
	point: number;
	championship?: ChampionshipRef | null;
}

// Una riga di mazzo: una carta con il numero di copie possedute.
export interface CardEntry {
	name: string;
	path: string;
	copies: number;
}

// Pilota con i suoi due mazzi (dettaglio) e il campionato attivo, se iscritto.
export interface PilotDetail extends Pilot {
	inventory: CardEntry[];
	game_deck: CardEntry[];
	championship: ChampionshipRef | null;
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

// Tipo di una pool di carte: modifiche o sponsor.
export type PoolKind = 'modifiche' | 'sponsor';

// Pool come appare nell'elenco: carte diverse e somma delle copie.
export interface Pool {
	id: number;
	name: string;
	kind: PoolKind;
	cards_count: number;
	copies_count: number;
}

// Pool con l'elenco delle sue carte.
export interface PoolDetail extends Pool {
	cards: CardEntry[];
}

// Esito della ricarica di una pool di base: carte aggiunte, rimosse (file sparito),
// già presenti e avvisi.
export interface ReloadResult {
	added: string[];
	removed: string[];
	already_present: number;
	warnings: string[];
}
