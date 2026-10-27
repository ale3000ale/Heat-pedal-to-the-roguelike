import type { CardEntry } from '$lib/types';

// Valuta con cui si paga un pacchetto: gold o punti sponsor.
export type Currency = 'gold' | 'sponsor';

// Carta uscita da un pacchetto o presente nell'inventario: stessi campi di CardEntry.
export type DrawnCard = CardEntry;

// Un negozio apribile dall'utente: un campionato attivo e i suoi piloti iscritti.
// Risposta di GET /api/me/shops.
export interface ShopPilotRef {
	id: number;
	name: string;
}

export interface ShopEntry {
	championship_id: number;
	championship_name: string;
	pilots: ShopPilotRef[];
}

export interface MyShops {
	shops: ShopEntry[];
}

// Pilota come lo vede il negozio, con i saldi.
export interface ShopPilot {
	id: number;
	name: string;
	gold: number;
	sponsor: number;
}

// Pacchetto in vendita; sold_out = "Terminato".
// image_path è relativo a /media/pack.
export interface ShopPack {
	id: number;
	name: string;
	image_path: string;
	currency: string;
	cost: number;
	modifiche_count: number;
	sponsor_count: number;
	filter_enabled: boolean;
	filter_text: string | null;
	sold_out: boolean;
}

// Risposta di GET /api/championships/{id}/shop.
export interface ShopView {
	championship_id: number;
	championship_name: string;
	pilot: ShopPilot | null;
	read_only: boolean;
	locked: boolean;
	packs: ShopPack[];
}

// Esito di POST /api/championships/{id}/shop/purchases.
export interface PurchaseResult {
	purchase_id: number;
	pack_name: string;
	currency: string;
	cost: number;
	cards_modifiche: DrawnCard[];
	cards_sponsor: DrawnCard[];
	gold: number;
	sponsor: number;
}

// Risposta di GET /api/championships/{id}/shop/inventory.
export interface ShopInventory {
	pilot_id: number;
	pilot_name: string;
	modifiche: DrawnCard[];
	sponsor: DrawnCard[];
}

// Un acquisto dello storico, con i valori del momento dell'acquisto.
export interface PurchaseItem {
	id: number;
	pack_name: string;
	currency: string;
	cost: number;
	purchased_at: string;
	cards_modifiche: DrawnCard[];
	cards_sponsor: DrawnCard[];
}

// Storico di un pilota; pilot_id è null se il pilota non esiste più.
export interface PilotHistory {
	pilot_id: number | null;
	pilot_name: string;
	purchases: PurchaseItem[];
}

export interface ShopHistory {
	pilots: PilotHistory[];
}
