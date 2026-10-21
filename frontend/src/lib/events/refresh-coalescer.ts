export interface RefreshOptions<T> {
	load: () => Promise<T>;
	apply: (value: T) => void;
	onError: (error: unknown) => void;
}

/**
 * Accorpa invalidazioni senza sovrapporre letture REST.
 * @param options Lettura senza effetti UI, applicazione sincrona ed errore osservabile.
 * @returns request attende lo svuotamento della coda; dispose invalida i risultati.
 * Una nuova invalidazione durante load scarta quel risultato e richiede un altro giro.
 * Gli errori vengono inoltrati a onError; non si modificano form o sessioni qui.
 */
export function createRefreshCoalescer<T>(options: RefreshOptions<T>) {
	let disposed = false;
	let dirty = false;
	let running: Promise<void> | null = null;

	async function drain(): Promise<void> {
		while (dirty && !disposed) {
			dirty = false;
			try {
				const value = await options.load();
				if (!disposed && !dirty) options.apply(value);
			} catch (error) {
				if (disposed) return;
				try {
					options.onError(error);
				} catch (handlerError) {
					console.error('Errore nel gestore della rilettura', handlerError);
				}
			}
		}
	}

	function request(): Promise<void> {
		if (disposed) return Promise.resolve();
		dirty = true;
		if (running === null) {
			running = drain().finally(() => {
				running = null;
			});
		}
		return running;
	}

	function dispose(): void {
		disposed = true;
		dirty = false;
	}

	return { request, dispose };
}
