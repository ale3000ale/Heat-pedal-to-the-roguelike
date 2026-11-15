import { createRefreshCoalescer } from '../../events/refresh-coalescer';

export interface AdminCardLiveRefreshOptions<T> {
	load: () => Promise<T>;
	apply: (snapshot: T) => void;
	getState: () => { busy: boolean; preserve: boolean };
	onStale: () => void;
	onError: (error: unknown) => void;
}

type LiveRead<T> =
	{ revision: number; ok: true; value: T } | { revision: number; ok: false; error: unknown } | null;

/**
 * Accorpa riletture live con il coordinatore condiviso, senza timer o scritture.
 * @param options Loader senza effetti, stato corrente e callback sincrone.
 * @returns Invalidazione, notifica stato, accettazione server esplicita e cleanup.
 * Non sostituisce bozze protette; il consumatore decide come mostrare il blocco.
 * load/apply falliti passano a onError senza retry automatici. Nessuna richiesta iniziale implicita.
 */
export function createAdminCardLiveRefresh<T>(options: AdminCardLiveRefreshOptions<T>) {
	let disposed = false;
	let pending = false;
	let held = false;
	let reading = false;
	let revision = 0;

	const coalescer = createRefreshCoalescer<LiveRead<T>>({
		load: async () => {
			const state = options.getState();
			if (disposed || held || state.busy || state.preserve) return null;
			pending = false;
			reading = true;
			const captured = revision;
			try {
				const value = await options.load();
				return { revision: captured, ok: true, value };
			} catch (error) {
				return { revision: captured, ok: false, error };
			} finally {
				reading = false;
			}
		},
		apply: (result) => {
			if (disposed) return;
			if (result === null) {
				void schedule();
				return;
			}
			const state = options.getState();
			if (result.revision !== revision || pending || held || state.busy || state.preserve) {
				pending = true;
				void schedule();
				return;
			}
			if (result.ok) options.apply(result.value);
			else options.onError(result.error);
		},
		onError: (error) => {
			if (!disposed) options.onError(error);
		}
	});

	function schedule(): Promise<void> {
		if (disposed || held || !pending) return Promise.resolve();
		const state = options.getState();
		if (state.busy) return Promise.resolve();
		if (state.preserve) {
			held = true;
			options.onStale();
			return Promise.resolve();
		}
		return coalescer.request();
	}

	/** Accoda un segnale remoto; attende solo le letture attualmente eseguibili. */
	function invalidate(): Promise<void> {
		if (disposed) return Promise.resolve();
		revision += 1;
		pending = true;
		return schedule();
	}

	/** Chiamare dopo cambi di bozza o busy; non libera un blocco per semplice reset locale. */
	function stateChanged(): void {
		if (disposed) return;
		if (options.getState().busy) {
			revision += 1;
			if (reading) pending = true;
			return;
		}
		void schedule();
	}

	/**
	 * Libera il blocco solo dopo applicazione esplicita di una risposta server utilizzabile.
	 * Invalida letture precedenti e conserva eventuali segnali accodati durante PUT/GET.
	 * Non chiamare per reset, errori o semplice aggiornamento dello stato trasporto.
	 */
	function acceptServerSnapshot(): void {
		if (disposed) return;
		revision += 1;
		held = false;
		void schedule();
	}

	/** Invalida risultati futuri senza annullare la rete gia' partita. */
	function dispose(): void {
		if (disposed) return;
		disposed = true;
		pending = false;
		coalescer.dispose();
	}

	return { invalidate, stateChanged, acceptServerSnapshot, dispose };
}
