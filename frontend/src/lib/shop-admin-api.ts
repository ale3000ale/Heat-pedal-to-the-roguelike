import { api, ApiError } from '$lib/api';
import type {
	PackData,
	PackImage,
	PackTemplate,
	ShopTemplate,
	ShopTemplateData
} from '$lib/shop-admin-types';

// Servizio API dell'area admin del Negozio (prefisso /api/shop, solo admin).
// Tutte le funzioni lanciano ApiError se la richiesta fallisce.

// Elenco dei template di pacchetto.
export function listPackTemplates(): Promise<PackTemplate[]> {
	return api<PackTemplate[]>('/shop/pack-templates');
}

// Crea un template di pacchetto. Errori: 422 per dati o immagine non validi.
export function createPackTemplate(data: PackData): Promise<PackTemplate> {
	return api<PackTemplate>('/shop/pack-templates', { method: 'POST', body: data });
}

// Modifica per intero un template. Errori: 404 assente, 422 dati non validi.
export function updatePackTemplate(id: number, data: PackData): Promise<PackTemplate> {
	return api<PackTemplate>(`/shop/pack-templates/${id}`, { method: 'PUT', body: data });
}

// Elimina un template e lo toglie dai template di negozio. Errori: 404 assente.
export function deletePackTemplate(id: number): Promise<void> {
	return api(`/shop/pack-templates/${id}`, { method: 'DELETE' });
}

// Elenco dei template di negozio, con l'indicatore "vuoto".
export function listShopTemplates(): Promise<ShopTemplate[]> {
	return api<ShopTemplate[]>('/shop/shop-templates');
}

// Crea un template di negozio. Errori: 404 template di pacchetto assente,
// 409 nome in uso, 422 nessun pacchetto o pacchetto ripetuto.
export function createShopTemplate(data: ShopTemplateData): Promise<ShopTemplate> {
	return api<ShopTemplate>('/shop/shop-templates', { method: 'POST', body: data });
}

// Rinomina un template di negozio e ne sostituisce i pacchetti (l'elenco può essere vuoto).
// Errori: 404, 409 nome in uso, 422 pacchetto ripetuto.
export function updateShopTemplate(id: number, data: ShopTemplateData): Promise<ShopTemplate> {
	return api<ShopTemplate>(`/shop/shop-templates/${id}`, { method: 'PUT', body: data });
}

// Elimina un template di negozio; i template di pacchetto restano. Errori: 404.
export function deleteShopTemplate(id: number): Promise<void> {
	return api(`/shop/shop-templates/${id}`, { method: 'DELETE' });
}

// Immagini disponibili per i pacchetti.
export function listPackImages(): Promise<PackImage[]> {
	return api<PackImage[]>('/shop/images');
}

// Messaggio d'errore del caricamento: il corpo è un file, quindi non passa da api().
function uploadMessage(status: number, data: unknown): string {
	if (data && typeof data === 'object' && 'detail' in data) {
		const detail = (data as { detail: unknown }).detail;
		if (typeof detail === 'string') return detail;
	}
	if (status === 413) return 'File troppo grande (massimo 5 MB)';
	return `Errore ${status}`;
}

// Carica un'immagine (png, jpg o webp, massimo 5 MB): il corpo è il file stesso e il
// nome viaggia nel parametro `filename`.
// Errori: 413 file troppo grande, 422 immagine non valida, 0 server non raggiungibile.
export async function uploadPackImage(file: File): Promise<PackImage> {
	let response: Response;
	try {
		response = await fetch(`/api/shop/images?filename=${encodeURIComponent(file.name)}`, {
			method: 'POST',
			headers: { Accept: 'application/json' },
			credentials: 'same-origin',
			body: file
		});
	} catch {
		throw new ApiError(0, 'Server non raggiungibile');
	}
	const data: unknown = await response.json().catch(() => null);
	if (!response.ok) throw new ApiError(response.status, uploadMessage(response.status, data));
	return data as PackImage;
}
