import type { Championship, Pilot } from '../types';

// Le tre sezioni a scomparsa della pagina Campionati.
export type GroupKey = 'enrolled' | 'active' | 'closed';

// Campionati divisi per sezione: Iscritto, Attivi e Chiusi.
export type ChampionshipGroups = Record<GroupKey, Championship[]>;

/**
 * Raccoglie gli id dei campionati attivi a cui è iscritto almeno un pilota.
 *
 * @param pilots Piloti dell'utente loggato, come li restituisce GET /pilots.
 * @returns Insieme di id senza duplicati; vuoto se nessun pilota è iscritto.
 */
export function enrolledChampionshipIds(pilots: Pilot[]): Set<number> {
	const ids = new Set<number>();
	for (const pilot of pilots) {
		if (pilot.championship) ids.add(pilot.championship.id);
	}
	return ids;
}

/**
 * Divide i campionati nelle tre sezioni della pagina.
 * - enrolled: campionati attivi con almeno un pilota dell'utente iscritto.
 * - active: gli altri campionati attivi (quelli già in enrolled non si ripetono).
 * - closed: tutti i campionati chiusi, anche quelli a cui l'utente partecipava.
 *
 * @param championships Tutti i campionati, attivi e chiusi.
 * @param pilots Piloti dell'utente loggato.
 * @returns I campionati divisi per sezione, nell'ordine ricevuto.
 */
export function groupChampionships(
	championships: Championship[],
	pilots: Pilot[]
): ChampionshipGroups {
	const enrolledIds = enrolledChampionshipIds(pilots);
	const open = championships.filter((c) => !c.is_closed);
	return {
		enrolled: open.filter((c) => enrolledIds.has(c.id)),
		active: open.filter((c) => !enrolledIds.has(c.id)),
		closed: championships.filter((c) => c.is_closed)
	};
}

/**
 * Sceglie l'unica sezione aperta all'arrivo sulla pagina.
 *
 * @param groups Campionati già divisi per sezione.
 * @returns 'enrolled' se l'utente ha almeno un pilota iscritto, altrimenti 'active'.
 */
export function initiallyOpenGroup(groups: ChampionshipGroups): GroupKey {
	return groups.enrolled.length > 0 ? 'enrolled' : 'active';
}
