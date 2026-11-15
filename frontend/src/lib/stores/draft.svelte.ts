import { createDraftSession } from '../draft/draft-session';
import type { DraftSessionOptions, DraftSessionState } from '../draft/draft-session';
import type { DraftCommands } from '../draft/draft-types';
import { parseDraft } from '../draft/draft-validation';

/** Adattatore reattivo per una sola sessione, senza singleton o rete iniziale.
 * Il chiamante fornisce il contesto autenticato e gestisce il lifecycle.
 * La costruzione propaga RangeError/TypeError dal controller per opzioni invalide.
 */
export class DraftStore {
	private session: ReturnType<typeof createDraftSession>;
	private view = $state.raw<DraftSessionState>({
		status: 'empty',
		snapshot: null,
		block: null,
		error: null,
		completion: null,
		raceId: null
	});
	private zoomed = $state.raw<{
		draftId: number;
		championshipId: number;
		slotId: number;
		name: string;
		path: string;
	} | null>(null);

	constructor(options: DraftSessionOptions) {
		this.session = createDraftSession(options);
		this.sync();
	}

	/** Vista indipendente: le modifiche del consumatore non alterano store o controller. */
	get state(): DraftSessionState {
		const view = this.view;
		return { ...view, snapshot: view.snapshot ? parseDraft(view.snapshot) : null };
	}

	get busy(): boolean {
		return this.view.status === 'loading' || this.view.status === 'writing';
	}

	get blocked(): boolean {
		return this.view.status === 'blocked';
	}

	/** Restituisce lo slot ingrandito valido o null, senza effetti o rete.
	 * L'identita include preparazione, campionato e copia/nome/percorso, non turno,
	 * versione, preview o chosen_by. Nessun permesso di scrittura e derivato dallo zoom.
	 */
	get zoomedSlotId(): number | null {
		const selected = this.zoomed;
		const draft = this.view.snapshot;
		if (
			!selected ||
			!draft ||
			draft.phase !== 'picking' ||
			this.view.block === 'authorization' ||
			selected.draftId !== draft.id ||
			selected.championshipId !== draft.championship_id
		)
			return null;
		const slot = draft.cards.find((card) => card.slot_id === selected.slotId);
		return slot?.name === selected.name && slot?.path === selected.path ? selected.slotId : null;
	}

	/** Alterna soltanto lo zoom locale della copia indicata.
	 * @param slotId ID di una copia presente nello snapshot picking corrente.
	 * @returns true se applicato, false senza contesto utilizzabile, se busy/bloccato
	 * o se lo slot e assente. Nessun GET/POST, mutazione del DTO o errore previsto.
	 * Lo stato appartiene all'istanza, quindi sopravvive al solo rimontaggio del picking.
	 */
	toggleZoom(slotId: number): boolean {
		this.syncContext();
		const draft = this.view.snapshot;
		if (this.busy || this.blocked || !draft || draft.phase !== 'picking') return false;
		const slot = draft.cards.find((card) => card.slot_id === slotId);
		if (!slot) return false;
		this.zoomed =
			this.zoomedSlotId === slotId
				? null
				: {
						draftId: draft.id,
						championshipId: draft.championship_id,
						slotId,
						name: slot.name,
						path: slot.path
					};
		return true;
	}

	private sync(): void {
		this.view = this.session.getState();
		// Non azzerare durante preview/refresh: eliminare solo un'identita non piu valida.
		if (this.zoomed !== null && this.zoomedSlotId === null) this.zoomed = null;
	}

	/** Pubblica stato iniziale e finale dell'operazione; non gestisce una seconda coda.
	 * Gli errori applicativi vengono gia classificati dal controller. Errori imprevisti
	 * del chiamante si propagano, ma il finally riallinea comunque la vista.
	 */
	private async run(operation: () => Promise<boolean>): Promise<boolean> {
		const pending = operation();
		try {
			this.sync();
			return await pending;
		} finally {
			this.sync();
		}
	}

	/** Rilettura esplicita, senza retry o caricamento implicito alla costruzione. */
	refresh(): Promise<boolean> {
		return this.run(() => this.session.refresh());
	}

	/** Delega payload e versione al controller; false se bloccato, fallito o obsoleto. */
	command<K extends keyof DraftCommands>(
		action: K,
		payload: Omit<DraftCommands[K], 'version'>
	): Promise<boolean> {
		return this.run(() => this.session.command(action, payload));
	}

	/** Da chiamare al cambio di autenticazione/ruolo/contesto, fuori dai getter di rendering.
	 * Non fa rete: pubblica l'eventuale invalidazione rilevata dal controller.
	 * Non sostituisce il collegamento lifecycle che dovra fare il futuro host.
	 */
	syncContext(): void {
		this.sync();
	}

	/** Dismette definitivamente e svuota vista e zoom; non annulla scritture gia inviate. */
	dispose(): void {
		this.session.dispose();
		this.sync();
	}
}
