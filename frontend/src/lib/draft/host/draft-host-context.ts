import { getContext, setContext } from 'svelte';
import type { createDraftHost } from './draft-host';

export type DraftHost = ReturnType<typeof createDraftHost>;
const KEY = Symbol('heat-draft-host');

/** Registra l'istanza del layout durante l'inizializzazione del componente.
 * Non crea un singleton, non effettua richieste e restituisce la stessa istanza.
 */
export function provideDraftHost(host: DraftHost): DraftHost {
	return setContext(KEY, host);
}

/** Recupera l'host durante l'inizializzazione di un discendente del layout.
 * @throws Error se il provider non e presente; non crea un registro alternativo.
 */
export function getDraftHost(): DraftHost {
	const host = getContext<DraftHost | undefined>(KEY);
	if (!host) throw new Error('Host draft assente nel contesto del layout');
	return host;
}
