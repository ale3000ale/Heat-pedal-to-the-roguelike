import { createDraftDeckSession } from './draft-deck-session';
import type { DraftDeckSession } from './draft-deck-session';
import type { DraftSessionState } from './draft-session';
import type { DraftStore } from './stores/draft.svelte';

export type DraftFlowScreen = 'loading' | 'start' | 'attendance' | 'order' | 'picking' | 'decks' | 'closed';

/** Deriva la schermata senza transizioni di gioco o rete.
 * attendanceDraftId e solo la scelta locale del percorso iniziale.
 * Nessuna deduzione di gara creata da tutti READY: valgono gli esiti del controller.
 */
export function draftFlowView(state: DraftSessionState, attendanceDraftId: number | null, externalBusy = false) {
	const closed = state.status === 'finished' || state.status === 'disposed';
	let screen: DraftFlowScreen = 'loading';
	if (closed) screen = 'closed';
	else if (state.snapshot) {
		screen = state.snapshot.phase === 'attendance'
			? state.snapshot.id === attendanceDraftId ? 'attendance' : 'start'
			: state.snapshot.phase;
	}
	return {
		screen,
		visible: !closed,
		busy: !closed && (externalBusy || state.status === 'loading' || state.status === 'writing'),
		completion: state.status === 'finished' ? state.completion : null,
		raceId: state.status === 'finished' ? state.raceId : null
	};
}

export interface DraftFlowContext {
	owner: DraftStore;
	draftId: number;
	decks: DraftDeckSession;
	dispose: () => void;
}

/** Crea il coordinatore del mazzo per una preparazione gia caricata, senza GET.
 * Null senza snapshot o dopo conclusione/dispose. Il consumatore conserva questa
 * istanza per owner/ID, non per versione. dispose elimina solo i dettagli del mazzo;
 * il componente proprietario dismette separatamente lo store principale.
 */
export function createDraftFlowContext(store: DraftStore): DraftFlowContext | null {
	const state = store.state;
	if (!state.snapshot || state.status === 'finished' || state.status === 'disposed') return null;
	const draftId = state.snapshot.id;
	const decks = createDraftDeckSession({ store, draftId });
	return { owner: store, draftId, decks, dispose: () => decks.dispose() };
}
