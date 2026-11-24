import { describe, expect, it } from 'vitest';
import {
	genericCardImageUrl,
	mapCountLabel,
	nextRaceImageUrl,
	nextRaceName
} from './next-race-setup';

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

	it('costruisce gli URL delle miniature generiche', () => {
		expect(genericCardImageUrl('stress')).toBe('/media/cards/generics/stress.webp');
		expect(genericCardImageUrl('heat')).toBe('/media/cards/generics/heat.webp');
	});

	it('mostra un trattino quando il conteggio non e disponibile', () => {
		expect(mapCountLabel(0)).toBe('0');
		expect(mapCountLabel(7)).toBe('7');
		expect(mapCountLabel(null)).toBe('—');
		expect(mapCountLabel(undefined)).toBe('—');
		expect(mapCountLabel(-1)).toBe('—');
	});
});
