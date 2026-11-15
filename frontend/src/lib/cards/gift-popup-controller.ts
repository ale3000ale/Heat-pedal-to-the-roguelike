import { reconcileGifts } from './gift-reconcile';
import type { PilotGiftNotification } from './gift-notifications-api';

type Notification = PilotGiftNotification;

export interface GiftPopupOptions {
	acknowledge: (shown: readonly Notification[]) => Promise<void>;
	onChange: (visible: readonly Notification[]) => void;
	onError: (error: unknown) => void;
}

/**
 * Gestisce una sequenza di popup senza conferme automatiche agli annullamenti.
 * @param options Conferma selettiva e callback di presentazione/errore del chiamante.
 * @returns update per snapshot completi, close per gli ID resi e dispose per il contesto.
 * Non legge REST, non crea timer e non dipende da Svelte. Le callback devono essere sincrone.
 * Il chiamante deve fornire solo snapshot riusciti e gli ID resi dal componente popup.
 */
export function createGiftPopupController(options: GiftPopupOptions) {
	let latest: Notification[] = [];
	let visible: Notification[] = [];
	const hidden = new Set<number>();
	let closing = false;
	let disposed = false;

	/**
	 * Riconcilia lo snapshot senza confermare notifiche e conserva i nuovi arrivi in coda.
	 * @param snapshot Notifiche complete del medesimo campionato e utente.
	 * @returns Nessun valore; onChange riceve una nuova copia della lista visibile.
	 */
	function update(snapshot: readonly Notification[]): void {
		if (disposed) return;
		latest = [...snapshot];
		if (closing) return;
		const candidates = latest.filter(({ gift }) => !hidden.has(gift.id));
		const byId = new Map(candidates.map((entry) => [entry.gift.id, entry]));
		const reconciled = reconcileGifts(
			visible.map(({ gift }) => gift),
			candidates.map(({ gift }) => gift)
		);
		visible = reconciled.visible.length
			? reconciled.visible.map((gift) => byId.get(gift.id)!)
			: candidates;
		options.onChange([...visible]);
	}

	/**
	 * Chiude per richiesta dell'utente e conferma soltanto ID visibili e gia' resi.
	 * @param shownIds ID dell'ultima lista effettivamente resa dal popup, non della coda.
	 * @returns Si risolve dopo il tentativo; gli errori API sono passati a onError.
	 * Se alcuni batch falliscono, lo snapshot seguente resta la fonte autorevole.
	 * Non cancella richieste gia' partite; dispose impedisce gli effetti UI successivi.
	 */
	async function close(shownIds: readonly number[]): Promise<void> {
		if (disposed || closing) return;
		const shown = new Set(shownIds);
		const selected = visible.filter(({ gift }) => shown.has(gift.id));
		selected.forEach(({ gift }) => hidden.add(gift.id));
		visible = [];
		closing = true;
		options.onChange([]);
		try {
			if (selected.length) await options.acknowledge(selected);
		} catch (error) {
			if (!disposed) {
				selected.forEach(({ gift }) => hidden.delete(gift.id));
				options.onError(error);
			}
		} finally {
			if (!disposed) {
				closing = false;
				update(latest);
			}
		}
	}

	/**
	 * Ferma gli effetti locali del vecchio contesto; non invia conferme o callback.
	 * @returns Nessun valore. Operazione idempotente, non annulla HTTP gia' partite.
	 */
	function dispose(): void {
		disposed = true;
		latest = [];
		visible = [];
		hidden.clear();
	}

	return { update, close, dispose };
}
