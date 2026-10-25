import type { DraftHostEntry } from './draft-host';
import type { DraftStore } from './stores/draft.svelte';

function eligible(entry: DraftHostEntry, known: boolean): boolean {
	const root = entry.store.state;
	if (root.status === 'finished' || root.status === 'disposed' || root.block === 'authorization') return false;
	if (!root.snapshot) return known;
	const dto = root.snapshot;
	if (dto.can_manage) return true;
	return (dto.phase === 'picking' || dto.phase === 'decks') &&
		dto.participants.some((pilot) => pilot.present && dto.my_pilot_ids.includes(pilot.pilot_id));
}

/** Mantiene l'ordine di ingresso locale e aggiunge in fondo le nuove istanze autorizzate.
 * Non cambia il turno server o i permessi. Un aggiornamento di versione non sposta
 * lo store attivo. Termini, dismissioni, perdita di accesso e rimozioni liberano la coda.
 * Restituisce previous se le identita non cambiano, evitando effetti reattivi ciclici.
 */
export function reconcileDraftQueue(previous: readonly DraftStore[], entries: readonly DraftHostEntry[]): readonly DraftStore[] {
	const allowed = new Set(entries.filter((entry) => eligible(entry, previous.includes(entry.store))).map((entry) => entry.store));
	const next = previous.filter((store) => allowed.has(store));
	for (const entry of entries) if (allowed.has(entry.store) && !next.includes(entry.store)) next.push(entry.store);
	return next.length === previous.length && next.every((store, index) => store === previous[index]) ? previous : next;
}

/** Seleziona la testa della coda senza mutare registri o effettuare rete. */
export function selectDraftEntry(queue: readonly DraftStore[], entries: readonly DraftHostEntry[]): DraftHostEntry | null {
	return entries.find((entry) => entry.store === queue[0]) ?? null;
}

/** Sopprime Escape prima dei listener window dei modal sospesi, senza inviare cancel. */
export function blockDraftEscape(
	event: Pick<KeyboardEvent, 'key' | 'preventDefault' | 'stopImmediatePropagation'>,
	blocked: boolean
): void {
	if (!blocked || event.key !== 'Escape') return;
	event.preventDefault();
	event.stopImmediatePropagation();
}
