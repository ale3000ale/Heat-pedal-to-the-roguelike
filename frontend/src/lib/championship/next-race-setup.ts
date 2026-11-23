/**
 * Deriva etichetta e URL pubblico di una carta estratta per la prossima gara.
 * @param path Percorso relativo a media, oppure null se il setup non e' pronto.
 * @returns Nome del file senza estensione, oppure null. Il nome resta quello del disco.
 */
export function nextRaceName(path: string | null): string | null {
	if (!path) return null;
	const file = path.split(/[\\/]/).pop() ?? path;
	return file.replace(/\.webp$/i, '');
}

/**
 * @param path Percorso relativo a media, oppure null se il setup non e' pronto.
 * @returns URL servito dal mount /media, oppure null.
 */
export function nextRaceImageUrl(path: string | null): string | null {
	return path ? `/media/${path.replace(/\\/g, '/')}` : null;
}
