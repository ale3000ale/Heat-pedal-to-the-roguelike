import type { DraftDeckSession } from './draft-deck-session';
import type { DraftStore } from './stores/draft.svelte';

/** Riconcilia un dettaglio gia caricato dopo una lettura autorevole della preparazione.
 * Nessuna GET iniziale duplicata, nessun POST, un tentativo per coordinatore/pilota/versione.
 * false significa non necessario, non avviabile o lettura fallita; mai rollback.
 * I fallimenti restano nel coordinatore e consentono Rileggi mazzo esplicito.
 */
export function createDraftLiveDeckRefresh() {
	const attempted = new WeakMap<DraftDeckSession, { pilotId: number; version: number }>();
	async function refresh(owner: DraftStore, decks: DraftDeckSession): Promise<boolean> {
		owner.syncContext();
		const root = owner.state;
		const detail = decks.getState();
		if (
			decks.owner !== owner ||
			root.status !== 'idle' ||
			root.snapshot?.phase !== 'decks' ||
			decks.draftId !== root.snapshot.id ||
			detail.busy ||
			detail.status === 'disposed' ||
			detail.pilotId === null ||
			!detail.data
		)
			return false;
		const version = root.snapshot.version;
		if (
			detail.data.preparation_version === version &&
			detail.data.ready === root.snapshot.ready.includes(detail.pilotId)
		)
			return false;
		const previous = attempted.get(decks);
		if (previous?.pilotId === detail.pilotId && previous.version === version) return false;
		attempted.set(decks, { pilotId: detail.pilotId, version });
		return decks.reload();
	}
	return { refresh };
}
