import type { Currency } from '$lib/shop-types';
import type { PackData, PackFields } from '$lib/shop-admin-types';

// Costo di partenza di un nuovo pacchetto, per valuta (uguale al backend).
export const DEFAULT_PACK_COSTS: Record<Currency, number> = { gold: 10, sponsor: 2 };

// Stato del modulo di un pacchetto: testi e numeri come li modifica l'utente.
export interface PackForm {
	name: string;
	image_path: string;
	currency: Currency;
	cost: number;
	modifiche_count: number;
	sponsor_count: number;
	filter_enabled: boolean;
	filter_text: string;
}

// Modulo vuoto con i valori di partenza di un nuovo pacchetto (10 oro).
export function emptyPackForm(): PackForm {
	return {
		name: '',
		image_path: '',
		currency: 'gold',
		cost: DEFAULT_PACK_COSTS.gold,
		modifiche_count: 3,
		sponsor_count: 0,
		filter_enabled: false,
		filter_text: ''
	};
}

// Cambio di valuta: se il costo è ancora quello predefinito della valuta precedente
// passa a quello della nuova (10 oro, 2 sponsor); un costo scelto a mano resta com'è.
export function costAfterCurrencyChange(cost: number, from: Currency, to: Currency): number {
	return cost === DEFAULT_PACK_COSTS[from] ? DEFAULT_PACK_COSTS[to] : cost;
}

// Modulo precompilato da un pacchetto o da un template esistente.
export function formFromPack(pack: PackFields): PackForm {
	return {
		name: pack.name,
		image_path: pack.image_path,
		currency: pack.currency === 'sponsor' ? 'sponsor' : 'gold',
		cost: pack.cost,
		modifiche_count: pack.modifiche_count,
		sponsor_count: pack.sponsor_count,
		filter_enabled: pack.filter_enabled,
		filter_text: pack.filter_text ?? ''
	};
}

// Vero se il valore è un intero non inferiore al minimo (un campo vuoto non lo è).
function isWhole(value: unknown, min: number): boolean {
	return typeof value === 'number' && Number.isInteger(value) && value >= min;
}

// Vero se il testo del filtro contiene almeno un nome (nomi separati da virgola).
function hasFilterTerms(text: string): boolean {
	return text.split(',').some((term) => term.trim() !== '');
}

// Controlla il modulo con le stesse regole del backend (`PackData`).
// Restituisce il messaggio del primo errore, oppure null se il modulo è valido.
export function validatePackForm(form: PackForm): string | null {
	const name = form.name.trim();
	if (name.length < 1 || name.length > 40) {
		return 'Nome obbligatorio, massimo 40 caratteri.';
	}
	if (!isWhole(form.cost, 1)) {
		return 'Il costo deve essere un intero maggiore di 0.';
	}
	if (!isWhole(form.modifiche_count, 0) || !isWhole(form.sponsor_count, 0)) {
		return 'Le quantità di carte devono essere interi da 0.';
	}
	if (form.modifiche_count + form.sponsor_count < 1) {
		return 'Il pacchetto deve contenere almeno una carta.';
	}
	if (form.filter_enabled && !hasFilterTerms(form.filter_text)) {
		return 'Il filtro attivo richiede almeno un nome.';
	}
	return null;
}

// Converte il modulo (già validato) nei dati da inviare al backend.
export function toPackData(form: PackForm): PackData {
	const filterText = form.filter_text.trim();
	return {
		name: form.name.trim(),
		image_path: form.image_path === '' ? null : form.image_path,
		currency: form.currency,
		cost: form.cost,
		modifiche_count: form.modifiche_count,
		sponsor_count: form.sponsor_count,
		filter_enabled: form.filter_enabled,
		filter_text: filterText === '' ? null : filterText
	};
}

// Controlla nome e pacchetti di un template di negozio.
// `requirePacks` è vero in creazione (serve almeno un pacchetto); in modifica l'elenco
// può essere vuoto. Restituisce il messaggio dell'errore, oppure null.
export function validateShopTemplate(
	name: string,
	packTemplateIds: number[],
	requirePacks: boolean
): string | null {
	const clean = name.trim();
	if (clean.length < 2 || clean.length > 40) {
		return 'Nome obbligatorio, da 2 a 40 caratteri.';
	}
	if (requirePacks && packTemplateIds.length === 0) {
		return 'Serve almeno un template di pacchetto.';
	}
	return null;
}
