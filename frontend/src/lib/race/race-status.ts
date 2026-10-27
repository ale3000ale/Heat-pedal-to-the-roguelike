import type { RaceStatus } from '$lib/race/race-types';

// Come si mostra lo stato di una gara: testo e classe del colore.
export interface RaceStatusView {
	label: string;
	class: string;
}

// Gli stati dell'app sono tre: in corso, in revisione, terminata. "Da rivedere" (risultati
// registrati, revisione delle carte non ancora aperta) si mostra come "in revisione".
const VIEWS: Record<RaceStatus, RaceStatusView> = {
	in_progress: { label: 'in corso', class: 'text-red-600' },
	in_review: { label: 'in revisione', class: 'text-amber-600' },
	to_review: { label: 'in revisione', class: 'text-amber-600' },
	closed: { label: 'terminata', class: 'text-green-600' }
};

/**
 * Etichetta e colore dello stato di una gara, uguali in ogni pagina.
 *
 * @param status Stato restituito dal backend.
 * @returns Testo da mostrare e classe CSS del colore.
 */
export function raceStatusView(status: RaceStatus): RaceStatusView {
	return VIEWS[status];
}
