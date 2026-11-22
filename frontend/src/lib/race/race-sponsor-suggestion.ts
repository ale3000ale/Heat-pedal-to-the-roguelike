import type { RaceResult } from './race-types';

/**
 * Punti sponsor da cui parte una riga del modulo risultati.
 * @param result Risultato del pilota nella gara.
 * @returns I punti salvati se la gara ha già una posizione, altrimenti il suggerimento
 * dei tasti S. Non scrive nulla: il valore resta modificabile e vale solo alla conferma.
 */
export function initialSponsor(
	result: Pick<RaceResult, 'position' | 'sponsor_points' | 'suggested_sponsor_points'>
): number {
	return result.position === null ? result.suggested_sponsor_points : result.sponsor_points;
}
