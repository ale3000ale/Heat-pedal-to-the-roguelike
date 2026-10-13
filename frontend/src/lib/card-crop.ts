// Misure esatte che il backend richiede per una carta (larghezza, altezza in pixel).
export const CARD_WIDTH = 560;
export const CARD_HEIGHT = 870;
// Zoom massimo oltre quello che copre l'area (1 = l'immagine riempie giusto la carta).
export const MAX_ZOOM = 4;

// Stato del ritaglio: zoom e posizione dell'angolo in alto a sinistra dell'immagine,
// espressa in pixel dell'area della carta (0 o negativa: l'immagine esce dal bordo).
export interface CropView {
	zoom: number;
	x: number;
	y: number;
}

// Porzione dell'immagine originale da disegnare sulla carta, in pixel dell'originale.
export interface SourceRect {
	sx: number;
	sy: number;
	sw: number;
	sh: number;
}

// Scala minima che fa coprire tutta la carta all'immagine.
// Parametri: width e height dell'immagine (maggiori di zero). Ritorna: il fattore di scala.
// Errori: RangeError se una misura non è positiva.
export function baseScale(width: number, height: number): number {
	if (!(width > 0) || !(height > 0)) throw new RangeError('Misure immagine non valide');
	return Math.max(CARD_WIDTH / width, CARD_HEIGHT / height);
}

// Tiene lo zoom tra 1 e MAX_ZOOM; un valore non numerico vale 1.
export function clampZoom(zoom: number): number {
	if (!Number.isFinite(zoom)) return 1;
	return Math.min(Math.max(zoom, 1), MAX_ZOOM);
}

// Limita la posizione perché l'immagine copra sempre tutta la carta (nessun bordo vuoto).
function clampAxis(value: number, drawn: number, area: number): number {
	return Math.min(0, Math.max(area - drawn, value));
}

// Dimensioni dell'immagine come appare sulla carta con lo zoom dato.
function drawnSize(width: number, height: number, zoom: number) {
	const scale = baseScale(width, height) * zoom;
	return { scale, w: width * scale, h: height * scale };
}

// Vista iniziale: zoom 1 con l'immagine centrata.
// Parametri: width e height dell'immagine. Errori: RangeError se le misure non sono valide.
export function initialView(width: number, height: number): CropView {
	const { w, h } = drawnSize(width, height, 1);
	return { zoom: 1, x: (CARD_WIDTH - w) / 2, y: (CARD_HEIGHT - h) / 2 };
}

// Sposta l'immagine di (dx, dy) pixel mantenendola dentro i limiti.
export function panView(view: CropView, dx: number, dy: number, width: number, height: number): CropView {
	const { w, h } = drawnSize(width, height, view.zoom);
	return {
		zoom: view.zoom,
		x: clampAxis(view.x + dx, w, CARD_WIDTH),
		y: clampAxis(view.y + dy, h, CARD_HEIGHT)
	};
}

// Cambia lo zoom tenendo fermo il punto che sta al centro della carta.
// Parametri: view, vista attuale; zoom, valore richiesto (viene limitato); width e height
// dell'immagine. Ritorna: la nuova vista, sempre dentro i limiti.
export function zoomView(view: CropView, zoom: number, width: number, height: number): CropView {
	const next = clampZoom(zoom);
	const before = drawnSize(width, height, view.zoom);
	const after = drawnSize(width, height, next);
	const centerX = (CARD_WIDTH / 2 - view.x) / before.scale;
	const centerY = (CARD_HEIGHT / 2 - view.y) / before.scale;
	return {
		zoom: next,
		x: clampAxis(CARD_WIDTH / 2 - centerX * after.scale, after.w, CARD_WIDTH),
		y: clampAxis(CARD_HEIGHT / 2 - centerY * after.scale, after.h, CARD_HEIGHT)
	};
}

// Porzione dell'immagine originale che finisce sulla carta nella vista data.
// Serve a disegnare il ritaglio finale a 560x870 sul canvas.
export function sourceRect(view: CropView, width: number, height: number): SourceRect {
	const { scale } = drawnSize(width, height, view.zoom);
	return {
		sx: -view.x / scale,
		sy: -view.y / scale,
		sw: CARD_WIDTH / scale,
		sh: CARD_HEIGHT / scale
	};
}
