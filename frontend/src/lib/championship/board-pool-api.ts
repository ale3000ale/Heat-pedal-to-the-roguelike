import { api } from '$lib/api';

// Pool di mappe o eventi di un campionato (solo admin).
export type BoardPoolKind = 'mappe' | 'eventi';

export interface BoardPoolField {
	label: string;
	value: string;
}

export interface BoardPoolCard {
	id: number;
	nome: string;
	image: string;
	// Falso quando la carta è già uscita dalla pool del campionato.
	in_pool: boolean;
	// Vero quando la carta è in pool ma non può essere estratta.
	blocked: boolean;
	fields: BoardPoolField[];
}

export interface BoardPoolCardPatch {
	in_pool?: boolean;
	blocked?: boolean;
}

export interface BoardPool {
	kind: BoardPoolKind;
	cards: BoardPoolCard[];
}

// Il percorso del JSON è relativo a backend/media, servito da /media.
export function boardPoolImageUrl(image: string): string {
	return `/media/${image.replace(/\\/g, '/')}`;
}

// Errori: ApiError se non sei admin (403) o il campionato non esiste (404).
export function fetchBoardPool(championshipId: number, kind: BoardPoolKind): Promise<BoardPool> {
	return api<BoardPool>(`/championships/${championshipId}/board-pools/${kind}`);
}

// Espelle/reinserisce una carta oppure la blocca/sblocca (solo admin).
export function updateBoardPoolCard(
	championshipId: number,
	kind: BoardPoolKind,
	cardId: number,
	patch: BoardPoolCardPatch
): Promise<BoardPoolCard> {
	return api<BoardPoolCard>(
		`/championships/${championshipId}/board-pools/${kind}/cards/${cardId}`,
		{ method: 'PATCH', body: patch }
	);
}
