import type { CardEntry } from '../../types';

/** Iscritto visibile all'admin nel contesto del campionato. */
export interface AdminPilotRead {
	pilot_id: number;
	name: string;
	user_id: number;
	username: string;
}

/** Pool assente e contenitore presente ma vuoto restano distinguibili. */
export interface AdminDeckRead {
	available: boolean;
	id: number | null;
	version: number | null;
	cards: CardEntry[];
}

/** Cinque contenitori distinti, senza sommare mazzo e inventario. */
export interface AdminCardContainers {
	game_deck: AdminDeckRead;
	modification_inventory: AdminDeckRead;
	sponsor_inventory: AdminDeckRead;
	modification_pool: AdminDeckRead;
	sponsor_pool: AdminDeckRead;
}

/** Snapshot REST; read_only e blocked_reason provengono dal backend. */
export interface AdminPilotCardsRead {
	championship_id: number;
	pilot: AdminPilotRead;
	read_only: boolean;
	blocked_reason: string | null;
	containers: AdminCardContainers;
}
