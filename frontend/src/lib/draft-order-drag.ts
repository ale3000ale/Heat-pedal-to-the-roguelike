export interface OrderDragRowOptions {
	pilotId: number;
	start: (event: PointerEvent, pilotId: number) => void;
}

/** Action client: tutta la scheda avvia il gesto, ma i controlli figli restano autonomi.
 * @param node Scheda del pilota, non il contenitore che cattura il puntatore.
 * @param options ID e callback aggiornati dal componente.
 * @returns Aggiornamento opzioni e cleanup del solo listener, senza rete o mutazioni.
 */
export function orderDragRow(node: HTMLElement, options: OrderDragRowOptions) {
	let current = options;
	function down(event: PointerEvent): void {
		if (
			event.target instanceof Element &&
			event.target.closest(
				'button,a,input,select,textarea,[contenteditable="true"],[data-no-order-drag]'
			)
		)
			return;
		current.start(event, current.pilotId);
	}
	node.addEventListener('pointerdown', down);
	return {
		update(value: OrderDragRowOptions) {
			current = value;
		},
		destroy() {
			node.removeEventListener('pointerdown', down);
		}
	};
}

/** Indice piu vicino al centro trascinato, usando le posizioni catturate all'inizio.
 * @param centers Centri verticali iniziali, strettamente crescenti e anche negativi.
 * @param from Indice iniziale del pilota, non quello risultante da un precedente move.
 * @param deltaY Spostamento del puntatore piu eventuale scorrimento del contenitore.
 * @param threshold Distanza minima per distinguere un gesto da un semplice clic.
 * @returns Indice limitato alle schede disponibili; non dipende dal DOM riordinato.
 * @throws RangeError per geometria, indice o distanze non validi.
 */
export function orderDragTarget(
	centers: readonly number[],
	from: number,
	deltaY: number,
	threshold = 6
): number {
	if (
		centers.length === 0 ||
		!Number.isInteger(from) ||
		from < 0 ||
		from >= centers.length ||
		!Number.isFinite(deltaY) ||
		!Number.isFinite(threshold) ||
		threshold < 0 ||
		centers.some(
			(value, index) => !Number.isFinite(value) || (index > 0 && value <= centers[index - 1])
		)
	) {
		throw new RangeError('Geometria del trascinamento ordine non valida');
	}
	if (Math.abs(deltaY) < threshold) return from;
	const position = centers[from] + deltaY;
	let target = from;
	let distance = Math.abs(deltaY);
	for (let index = 0; index < centers.length; index += 1) {
		const candidate = Math.abs(position - centers[index]);
		if (candidate < distance) {
			target = index;
			distance = candidate;
		}
	}
	return target;
}

/** Traslazione visiva della scheda trascinata rispetto al suo slot corrente.
 * @param centers Centri iniziali usati anche da orderDragTarget.
 * @param from Indice iniziale del gesto.
 * @param target Indice attuale della scheda nella bozza.
 * @param deltaY Spostamento del puntatore piu scorrimento del contenitore.
 * @returns Pixel da applicare con translateY perche la scheda resti sotto il puntatore.
 */
export function orderDragOffset(
	centers: readonly number[],
	from: number,
	target: number,
	deltaY: number
): number {
	if (centers[from] === undefined || centers[target] === undefined || !Number.isFinite(deltaY))
		throw new RangeError('Geometria del trascinamento ordine non valida');
	return deltaY - (centers[target] - centers[from]);
}

/** Limita lo spostamento perche la scheda resti nel rettangolo della lista dei piloti.
 * @param deltaY Spostamento del puntatore piu scorrimento del contenitore.
 * @param list Bordi verticali della lista all'inizio del gesto.
 * @param card Bordi verticali della scheda trascinata all'inizio del gesto.
 * @returns deltaY compreso tra il bordo superiore e quello inferiore della lista.
 */
export function orderDragClamp(
	deltaY: number,
	list: { top: number; bottom: number },
	card: { top: number; bottom: number }
): number {
	const min = Math.min(0, list.top - card.top);
	const max = Math.max(0, list.bottom - card.bottom);
	return Math.min(max, Math.max(min, deltaY));
}

/** Velocita di scorrimento automatico vicino ai bordi del contenitore.
 * @param clientY Posizione verticale del puntatore.
 * @param top Bordo superiore visibile del contenitore.
 * @param bottom Bordo inferiore visibile del contenitore.
 * @param edge Fascia sensibile in pixel.
 * @param max Pixel massimi per frame.
 * @returns Negativo verso l'alto, positivo verso il basso, zero fuori dalle fasce.
 */
export function orderAutoScrollStep(
	clientY: number,
	top: number,
	bottom: number,
	edge = 56,
	max = 14
): number {
	if (![clientY, top, bottom].every(Number.isFinite) || bottom <= top) return 0;
	const band = Math.min(edge, (bottom - top) / 3);
	if (band <= 0) return 0;
	if (clientY < top + band) return -Math.ceil(max * Math.min(1, (top + band - clientY) / band));
	if (clientY > bottom - band)
		return Math.ceil(max * Math.min(1, (clientY - (bottom - band)) / band));
	return 0;
}
