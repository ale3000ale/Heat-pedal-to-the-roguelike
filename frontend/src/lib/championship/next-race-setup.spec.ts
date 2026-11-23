import { describe, expect, it } from 'vitest';
import { nextRaceImageUrl, nextRaceName } from './next-race-setup';

describe('carte della prossima gara', () => {
	it('mostra il nome del file senza estensione', () => {
		expect(nextRaceName('board/maps/minimappe-page-0001.webp')).toBe('minimappe-page-0001');
		expect(nextRaceName('board/events/eventi-pages-to-jpg-0002.WEBP')).toBe(
			'eventi-pages-to-jpg-0002'
		);
	});

	it('restituisce null quando il setup non e pronto', () => {
		expect(nextRaceName(null)).toBeNull();
		expect(nextRaceImageUrl(null)).toBeNull();
	});

	it('costruisce l URL servito da media', () => {
		expect(nextRaceImageUrl('board/maps/minimappe-page-0001.webp')).toBe(
			'/media/board/maps/minimappe-page-0001.webp'
		);
		expect(nextRaceImageUrl('board\\events\\eventi-pages-to-jpg-0002.webp')).toBe(
			'/media/board/events/eventi-pages-to-jpg-0002.webp'
		);
	});
});
