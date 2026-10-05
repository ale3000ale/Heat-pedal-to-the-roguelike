import type { Standing } from './race-types';

// Chiave di una riga della classifica per il ciclo {#each}.
// Il rango non basta: i pari merito lo condividono. Nei campionati chiusi
// pilot_id può essere nullo: in quel caso usiamo rango e posizione nella lista.
export function standingKey(row: Standing, index: number): string {
	return row.pilot_id !== null ? `p${row.pilot_id}` : `r${row.rank}-${index}`;
}
