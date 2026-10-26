import { eventClient, type EventClient } from './events/event-client';
import type { DraftHost } from './draft-host-context';

export interface DraftLiveOptions {
	host: Pick<DraftHost, 'getState' | 'refresh'>;
	getContextKey: () => string | null;
	isBusy?: () => boolean;
	afterRefresh?: () => Promise<void>;
	onError: (cause: unknown) => void;
	client?: Pick<EventClient, 'subscribe'>;
}

/** Collega un registro allo stream esistente e avvia il recupero REST iniziale.
 * Accorpa segnali durante GET, POST e letture dettagli senza perdere l'invalidazione.
 * Il chiamante richiama wake quando termina busy. Nessun timer, polling, connect o POST.
 * request attende il drain avviabile, non attende indefinitamente un busy esterno.
 * Il registro applica direttamente le GET: non e una load pura per il coalescer generico.
 * @throws TypeError senza una generazione autenticata iniziale.
 */
export function startDraftLive(options: DraftLiveOptions) {
	const key = options.getContextKey();
	if (!key) throw new TypeError('Contesto live draft assente');
	let disposed = false;
	let dirty = false;
	let running: Promise<void> | null = null;
	let unsubscribe = () => {};

	function dispose(): void {
		if (disposed) return;
		disposed = true;
		dirty = false;
		unsubscribe();
	}
	function alive(): boolean {
		if (disposed) return false;
		if (options.getContextKey() !== key) {
			dispose();
			return false;
		}
		return true;
	}
	function blocked(): boolean {
		const state = options.host.getState();
		return (
			state.status === 'disposed' ||
			state.busy ||
			state.entries.some((entry) => entry.store.busy) ||
			(options.isBusy?.() ?? false)
		);
	}
	function report(cause: unknown): void {
		try {
			options.onError(cause);
		} catch (error) {
			console.error('Errore nel gestore live draft', error);
		}
	}
	async function drain(): Promise<void> {
		while (alive() && dirty && !blocked()) {
			dirty = false;
			const applied = await options.host.refresh();
			if (!alive()) return;
			if (applied) await options.afterRefresh?.();
			else if (blocked()) {
				dirty = true;
				return;
			}
		}
	}
	function wake(): Promise<void> {
		if (!alive() || !dirty || running || blocked()) return running ?? Promise.resolve();
		running = drain()
			.catch((cause) => {
				if (alive()) {
					dirty = false;
					report(cause);
				}
			})
			.finally(() => {
				running = null;
				// Copre anche un wake arrivato prima del finally dell'operazione precedente.
				if (alive() && dirty && !blocked()) void wake();
			});
		return running;
	}
	function request(): Promise<void> {
		if (!alive()) return Promise.resolve();
		dirty = true;
		return wake();
	}
	unsubscribe = (options.client ?? eventClient).subscribe((event) => {
		if (!alive()) return;
		if (event.type === 'auth.expired') {
			dispose();
			return;
		}
		if (event.type === 'draft.changed' || event.type === 'resync') void request();
	});
	if (disposed) unsubscribe();
	else void request();
	return {
		request,
		wake,
		dispose,
		getState: () => ({ pending: dirty, running: running !== null, disposed })
	};
}
