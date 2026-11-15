import { api, ApiError } from '$lib/api';
import type { PoolKind } from '$lib/types';

// Carta appena caricata, come la restituisce il backend.
export interface UploadedCard {
	name: string;
	path: string;
	copies: number;
	kind: PoolKind;
}

// Esito dell'eliminazione di una carta caricata: i file cancellati dal disco.
export interface DeletedCard {
	removed_files: string[];
}

// Indirizzo delle carte admin: tipo, nome e copie viaggiano nella query string.
function cardsUrl(params: Record<string, string>): string {
	return `/api/admin/cards?${new URLSearchParams(params).toString()}`;
}

// Ricava un messaggio leggibile dall'errore del backend ({"detail": "testo"}).
async function errorMessage(response: Response): Promise<string> {
	try {
		const data: unknown = await response.json();
		if (data && typeof data === 'object' && 'detail' in data) {
			const detail = (data as { detail: unknown }).detail;
			if (typeof detail === 'string') return detail;
		}
	} catch {
		// Corpo vuoto o non JSON: si usa il messaggio generico.
	}
	return response.status === 422 ? 'Dati non validi' : `Errore ${response.status}`;
}

// Carica una carta nella pool di base del tipo indicato (solo admin).
// Parametri: kind, tipo di pool; name, nome della carta; copies, numero di copie;
// image, immagine già tagliata a 560x870; doFetch, fetch alternativo (usato nei test).
// Ritorna: la carta creata. Errori: ApiError (stato 0 se il server non risponde;
// 409 nome già usato, 413 file troppo grande, 422 immagine non valida).
// L'immagine va nel corpo della richiesta così com'è, senza JSON: per questo non si
// usa api().
export async function uploadCard(
	kind: PoolKind,
	name: string,
	copies: number,
	image: Blob,
	doFetch: typeof fetch = fetch
): Promise<UploadedCard> {
	let response: Response;
	try {
		response = await doFetch(cardsUrl({ kind, name, copies: String(copies) }), {
			method: 'POST',
			headers: { Accept: 'application/json', 'Content-Type': image.type || 'image/webp' },
			credentials: 'same-origin',
			body: image
		});
	} catch {
		throw new ApiError(0, 'Server non raggiungibile');
	}
	if (!response.ok) throw new ApiError(response.status, await errorMessage(response));
	return (await response.json()) as UploadedCard;
}

// Elimina una carta caricata a mano dalla pool di base (solo admin).
// Errori: ApiError (404 carta assente, 409 carta non caricata a mano).
export function deleteCard(kind: PoolKind, name: string): Promise<DeletedCard> {
	const query = new URLSearchParams({ kind, name }).toString();
	return api<DeletedCard>(`/admin/cards?${query}`, { method: 'DELETE' });
}
