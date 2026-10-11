// Tipi dell'area admin del Negozio: specchio degli schemi del backend
// (`schemas/shop.py` e `schemas/pack.py`).
import type { Currency } from '$lib/shop-types';

// Dati inviati per creare o modificare un template di pacchetto o un pacchetto.
// `image_path` null = immagine predefinita.
export interface PackData {
	name: string;
	image_path: string | null;
	currency: Currency;
	cost: number;
	modifiche_count: number;
	sponsor_count: number;
	filter_enabled: boolean;
	filter_text: string | null;
}

// Caratteristiche di un pacchetto come le restituisce il backend.
export interface PackFields {
	name: string;
	image_path: string;
	currency: string;
	cost: number;
	modifiche_count: number;
	sponsor_count: number;
	filter_enabled: boolean;
	filter_text: string | null;
}

// Template di pacchetto (GET /api/shop/pack-templates).
export interface PackTemplate extends PackFields {
	id: number;
	created_at: string;
	updated_at: string;
}

// Immagine disponibile per i pacchetti; il percorso è relativo a /media/pack.
export interface PackImage {
	path: string;
}

// Template di negozio; `is_empty` = senza template di pacchetto (non utilizzabile).
export interface ShopTemplate {
	id: number;
	name: string;
	created_at: string;
	pack_template_ids: number[];
	is_empty: boolean;
}

// Dati inviati per creare o modificare un template di negozio.
export interface ShopTemplateData {
	name: string;
	pack_template_ids: number[];
}
