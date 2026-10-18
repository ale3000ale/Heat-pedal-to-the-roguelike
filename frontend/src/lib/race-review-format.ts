// Utility di formattazione per la revisione delle carte.

/**
 * Calcola i secondi che mancano alla scadenza della revisione.
 *
 * @param expiresAt scadenza in formato ISO, oppure null se la revisione non è attiva.
 * @param now istante di riferimento in millisecondi (iniettabile per i test).
 * @returns secondi rimanenti, mai negativi; 0 se la scadenza manca, è passata o non è valida.
 */
export function secondsLeft(expiresAt: string | null, now: number = Date.now()): number {
	if (!expiresAt) return 0;
	const end = Date.parse(expiresAt);
	if (Number.isNaN(end)) return 0;
	return Math.max(0, Math.ceil((end - now) / 1000));
}

/**
 * Formatta un numero di secondi come mm:ss.
 *
 * @param seconds secondi totali; i valori negativi o non finiti valgono 0.
 * @returns testo nel formato mm:ss, ad esempio "14:05".
 */
export function formatCountdown(seconds: number): string {
	const safe = Number.isFinite(seconds) && seconds > 0 ? Math.floor(seconds) : 0;
	const minutes = Math.floor(safe / 60);
	const rest = safe % 60;
	return `${String(minutes).padStart(2, '0')}:${String(rest).padStart(2, '0')}`;
}
