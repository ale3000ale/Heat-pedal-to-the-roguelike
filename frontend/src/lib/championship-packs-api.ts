import { api } from '$lib/api';
import type { PackData, PackFields } from '$lib/shop-admin-types';

// Servizio API dei pacchetti di un campionato (solo admin, prefisso /api/championships).
// Tutte le funzioni lanciano ApiError se la richiesta fallisce.

// Pacchetto del negozio di un campionato (copia indipendente del template di partenza).
export interface ChampionshipPack extends PackFields {
	id: number;
	championship_id: number;
	created_at: string;
	updated_at: string;
}

// Elenco dei pacchetti del campionato. Errori: 404 campionato assente.
export function listChampionshipPacks(championshipId: number): Promise<ChampionshipPack[]> {
	return api<ChampionshipPack[]>(`/championships/${championshipId}/packs`);
}

// Aggiunge un pacchetto. Per partire da un template si inviano i suoi valori, anche modificati.
// Errori: 404 campionato assente, 409 campionato chiuso, 422 dati o immagine non validi.
export function createChampionshipPack(
	championshipId: number,
	data: PackData
): Promise<ChampionshipPack> {
	return api<ChampionshipPack>(`/championships/${championshipId}/packs`, {
		method: 'POST',
		body: data
	});
}

// Modifica per intero un pacchetto.
// Errori: 404 campionato o pacchetto assente, 409 campionato chiuso, 422 dati non validi.
export function updateChampionshipPack(
	championshipId: number,
	packId: number,
	data: PackData
): Promise<ChampionshipPack> {
	return api<ChampionshipPack>(`/championships/${championshipId}/packs/${packId}`, {
		method: 'PUT',
		body: data
	});
}

// Elimina un pacchetto; lo storico degli acquisti resta.
// Errori: 404 campionato o pacchetto assente, 409 campionato chiuso.
export function deleteChampionshipPack(championshipId: number, packId: number): Promise<void> {
	return api(`/championships/${championshipId}/packs/${packId}`, { method: 'DELETE' });
}
