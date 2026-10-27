import type { AdminCardTransfer } from './admin-pilot-cards-draft';

/** Coppia attesa dal backend: interi positivi, ricontrollati nella transazione. */
export interface AdminExpectedDeckVersion {
	id: number;
	version: number;
}

/** Tutti i contenitori sono obbligatori; solo le due pool possono essere assenti. */
export interface AdminExpectedCardVersions {
	game_deck: AdminExpectedDeckVersion;
	modification_inventory: AdminExpectedDeckVersion;
	sponsor_inventory: AdminExpectedDeckVersion;
	modification_pool: AdminExpectedDeckVersion | null;
	sponsor_pool: AdminExpectedDeckVersion | null;
}

/** Contratto AdminPilotCardsSave: nessuna destinazione client o sostituzione carte. */
export interface AdminPilotCardsSave {
	versions: AdminExpectedCardVersions;
	transfers: AdminCardTransfer[];
}
