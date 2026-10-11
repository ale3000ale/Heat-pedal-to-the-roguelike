// Raggruppamento delle carte ottenute da un pacchetto per il riepilogo finale.

/** Voce minima raggruppabile: una carta (con percorso) e la sua sezione. */
export interface GroupableEntry {
	card: { path: string };
	section: string;
}

/** Voce raggruppata: la prima occorrenza e il numero di copie ottenute. */
export type GroupedEntry<T extends GroupableEntry> = { entry: T; copies: number };

/**
 * Raggruppa le carte uguali (stessa sezione e stesso percorso immagine).
 *
 * @param entries Carte nell'ordine di estrazione.
 * @returns Una voce per carta distinta, nell'ordine della prima uscita, con le copie.
 */
export function groupByCard<T extends GroupableEntry>(entries: T[]): GroupedEntry<T>[] {
	const groups = new Map<string, GroupedEntry<T>>();
	for (const entry of entries) {
		const key = `${entry.section}|${entry.card.path}`;
		const found = groups.get(key);
		if (found) found.copies += 1;
		else groups.set(key, { entry, copies: 1 });
	}
	return [...groups.values()];
}
