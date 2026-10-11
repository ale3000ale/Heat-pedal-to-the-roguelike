import { currencyLabel } from '$lib/shop-format';

// Riepilogo di un pacchetto: prezzo, valuta e numero di carte.
export function packSummary(pack: {
	cost: number;
	currency: string;
	modifiche_count: number;
	sponsor_count: number;
}): string {
	const price = `${pack.cost} ${currencyLabel(pack.currency)}`;
	return `${price} · ${pack.modifiche_count} modifiche · ${pack.sponsor_count} sponsor`;
}

// Testo d'errore da mostrare all'utente per qualunque eccezione.
export function errorMessage(e: unknown): string {
	return e instanceof Error ? e.message : 'Errore sconosciuto';
}
