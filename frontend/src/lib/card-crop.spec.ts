import { describe, expect, it } from 'vitest';
import {
	baseScale,
	CARD_HEIGHT,
	CARD_WIDTH,
	clampZoom,
	initialView,
	MAX_ZOOM,
	panView,
	sourceRect,
	zoomView
} from './card-crop';

describe('baseScale', () => {
	it('sceglie la scala che copre tutta la carta', () => {
		expect(baseScale(1120, 1740)).toBeCloseTo(0.5);
		expect(baseScale(2000, 870)).toBeCloseTo(1);
	});

	it('rifiuta misure non valide', () => {
		expect(() => baseScale(0, 100)).toThrow(RangeError);
	});
});

describe('clampZoom', () => {
	it('limita lo zoom tra 1 e il massimo', () => {
		expect(clampZoom(0.2)).toBe(1);
		expect(clampZoom(2)).toBe(2);
		expect(clampZoom(99)).toBe(MAX_ZOOM);
		expect(clampZoom(Number.NaN)).toBe(1);
	});
});

describe('initialView', () => {
	it('centra l\'immagine più larga della carta', () => {
		const view = initialView(1120, 1000);
		expect(view.zoom).toBe(1);
		expect(view.x).toBeCloseTo(-207.2);
		expect(view.y).toBeCloseTo(0);
	});
});

describe('panView', () => {
	it('non scopre mai i bordi', () => {
		const start = initialView(1120, 1000);
		const left = panView(start, 5000, 0, 1120, 1000);
		expect(left.x).toBe(0);
		const right = panView(start, -5000, 0, 1120, 1000);
		expect(right.x).toBeCloseTo(CARD_WIDTH - 1120 * baseScale(1120, 1000));
	});

	it('non sposta sull\'asse già a filo', () => {
		const start = initialView(1120, 1000);
		expect(panView(start, 0, 300, 1120, 1000).y).toBeCloseTo(0);
	});
});

describe('zoomView', () => {
	it('mantiene fermo il centro', () => {
		const start = initialView(1120, 1000);
		const before = sourceRect(start, 1120, 1000);
		const zoomed = zoomView(start, 2, 1120, 1000);
		const after = sourceRect(zoomed, 1120, 1000);
		const centerBefore = before.sx + before.sw / 2;
		const centerAfter = after.sx + after.sw / 2;
		expect(centerAfter).toBeCloseTo(centerBefore);
		expect(after.sw).toBeCloseTo(before.sw / 2);
	});

	it('limita lo zoom richiesto', () => {
		const start = initialView(1120, 1000);
		expect(zoomView(start, 50, 1120, 1000).zoom).toBe(MAX_ZOOM);
	});
});

describe('sourceRect', () => {
	it('a zoom 1 copre tutta l\'altezza dell\'immagine', () => {
		const rect = sourceRect(initialView(1120, 1000), 1120, 1000);
		expect(rect.sy).toBeCloseTo(0);
		expect(rect.sh).toBeCloseTo(1000);
		expect(rect.sw / rect.sh).toBeCloseTo(CARD_WIDTH / CARD_HEIGHT);
	});
});
