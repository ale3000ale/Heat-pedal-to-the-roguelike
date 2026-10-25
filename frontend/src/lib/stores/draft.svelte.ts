import { createDraftSession } from '../draft-session';
import type { DraftSessionOptions, DraftSessionState } from '../draft-session';
import type { DraftCommands } from '../draft-types';
import { parseDraft } from '../draft-validation';

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

	private sync(): void {
		this.view = this.session.getState();
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

	/** Dismette definitivamente e svuota la vista; non annulla scritture gia inviate. */
	dispose(): void {
		this.session.dispose();
		this.sync();
	}
}
