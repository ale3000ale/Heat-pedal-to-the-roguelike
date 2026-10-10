import { api } from '$lib/api';

// Pool complete di un campionato (solo admin): carte con copie rimaste e probabilità.
export interface ShopPoolCard {
	name: string;
	path: string;
	copies: number;
	// Percentuale di uscita alla prima estrazione, senza filtro.
	probability: number;
}

export interface ShopPoolSection {
	total_copies: number;
	cards: ShopPoolCard[];
}

export interface ShopPool {
	modifiche: ShopPoolSection;
	sponsor: ShopPoolSection;
}

// Errori: ApiError se non sei admin (403) o il campionato non esiste (404).
export function fetchShopPool(championshipId: number): Promise<ShopPool> {
	return api<ShopPool>(`/championships/${championshipId}/shop-pool`);
}
