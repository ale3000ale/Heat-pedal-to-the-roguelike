import type { RaceResult } from './race-types';

/**
 * Punti extra evento da cui parte una riga non ancora salvata del modulo risultati.
 * @param result Risultato del pilota: dopo il salvataggio si usano i punti già registrati.
 * @param position Posizione attuale della riga nel modulo, a partire da 1.
 * @param positionLimit Ultima posizione premiata dall'evento (0 se l'evento non premia).
 * @param positionPoints Punti extra per ogni posizione premiata.
 * @returns Il suggerimento; non scrive nulla e resta modificabile nel modulo.
 */
export function initialBonus(
	result: Pick<RaceResult, 'position' | 'bonus_points'>,
	position: number,
	positionLimit: number,
	positionPoints: number
): number {
	if (result.position !== null) return result.bonus_points;
	return position >= 1 && position <= positionLimit ? positionPoints : 0;
}
