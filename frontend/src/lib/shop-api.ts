import { api } from '$lib/api';
import type {
	MyShops,
	PurchaseResult,
	ShopHistory,
	ShopInventory,
	ShopView
} from '$lib/shop-types';

// Servizio API del negozio: una funzione per ogni rotta del backend.
// Tutte lanciano ApiError (vedi api.ts) se la richiesta fallisce.
// `fetchFn` è opzionale: serve ai test e alle funzioni `load` di SvelteKit.
type FetchFn = typeof fetch;

// Negozi apribili dall'utente (campionati attivi con almeno un suo pilota iscritto).
export function fetchMyShops(fetchFn?: FetchFn): Promise<MyShops> {
	return api<MyShops>('/me/shops', { fetch: fetchFn });
}

// Negozio di un campionato. Senza pilota (solo admin) è in sola lettura.
// Errori: 403 accesso non consentito o pilota non iscritto, 404 campionato o pilota assente.
export function fetchShop(
	championshipId: number,
	pilotId?: number,
	fetchFn?: FetchFn
): Promise<ShopView> {
	const query = pilotId === undefined ? '' : `?pilot_id=${pilotId}`;
	return api<ShopView>(`/championships/${championshipId}/shop${query}`, { fetch: fetchFn });
}

// Acquista un pacchetto con un proprio pilota iscritto.
// Errori: 409 per campionato chiuso, gara in corso, saldo insufficiente,
// pacchetto terminato o limite di copie raggiunto.
export function buyPack(
	championshipId: number,
	pilotId: number,
	packId: number,
	fetchFn?: FetchFn
): Promise<PurchaseResult> {
	return api<PurchaseResult>(`/championships/${championshipId}/shop/purchases`, {
		method: 'POST',
		body: { pilot_id: pilotId, pack_id: packId },
		fetch: fetchFn
	});
}

// Riepilogo delle carte del pilota per il popup del negozio.
export function fetchInventory(
	championshipId: number,
	pilotId: number,
	fetchFn?: FetchFn
): Promise<ShopInventory> {
	return api<ShopInventory>(`/championships/${championshipId}/shop/inventory?pilot_id=${pilotId}`, {
		fetch: fetchFn
	});
}

// Storico degli acquisti dei propri piloti, diviso per pilota.
export function fetchOwnHistory(championshipId: number, fetchFn?: FetchFn): Promise<ShopHistory> {
	return api<ShopHistory>(`/championships/${championshipId}/shop/history`, { fetch: fetchFn });
}

// Cronologia completa del campionato (solo admin).
export function fetchAllHistory(championshipId: number, fetchFn?: FetchFn): Promise<ShopHistory> {
	return api<ShopHistory>(`/championships/${championshipId}/shop/history/all`, {
		fetch: fetchFn
	});
}
