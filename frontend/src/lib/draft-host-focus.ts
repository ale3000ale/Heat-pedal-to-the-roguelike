const SELECTOR = 'a[href],button,input,select,textarea,[tabindex]';

/** Action client per il contenitore del solo flusso attivo.
 * @param node Contenitore con tabindex=-1, comprensivo degli errori recuperabili.
 * @returns Cleanup dei listener e ripristino differito se il vecchio focus e ancora valido.
 * Il focus automatico non richiede scroll. Tab conserva il comportamento di scorrimento
 * del browser per rendere visibili i controlli raggiunti dalla tastiera.
 * Nessun uso DOM all'importazione, nessuna richiesta e nessuna chiusura del modal.
 */
export function draftHostFocus(node: HTMLElement): { destroy: () => void } {
	const previous = document.activeElement instanceof HTMLElement ? document.activeElement : null;
	let alive = true;
	let moving = false;
	const controls = () =>
		[...node.querySelectorAll<HTMLElement>(SELECTOR)].filter(
			(element) =>
				element.tabIndex >= 0 &&
				!element.matches(':disabled') &&
				!element.closest('[inert]') &&
				element.getClientRects().length > 0
		);
	function focusFirst(): void {
		if (!alive || !node.isConnected || moving) return;
		moving = true;
		try {
			// Il recupero automatico del focus non deve riportare lo scroll alla prima carta.
			(controls()[0] ?? node).focus({ preventScroll: true });
		} finally {
			moving = false;
		}
	}
	function containFocus(event: FocusEvent): void {
		if (!(event.target instanceof Node) || !node.contains(event.target)) focusFirst();
	}
	function trapTab(event: KeyboardEvent): void {
		if (event.key !== 'Tab') return;
		const items = controls();
		const index = items.indexOf(document.activeElement as HTMLElement);
		if (items.length === 0) {
			event.preventDefault();
			node.focus();
		} else if (event.shiftKey && index <= 0) {
			event.preventDefault();
			items[items.length - 1].focus();
		} else if (!event.shiftKey && (index < 0 || index === items.length - 1)) {
			event.preventDefault();
			items[0].focus();
		}
	}
	node.addEventListener('keydown', trapTab);
	window.addEventListener('focusin', containFocus, true);
	queueMicrotask(focusFirst);
	return {
		destroy() {
			alive = false;
			node.removeEventListener('keydown', trapTab);
			window.removeEventListener('focusin', containFocus, true);
			// Attende la rimozione di inert; non sottrae focus a un altro draft accodato.
			queueMicrotask(() => {
				const current = document.activeElement;
				if (
					previous?.isConnected &&
					!previous.closest('[inert]') &&
					(current === document.body || current === null || node.contains(current))
				)
					previous.focus({ preventScroll: true });
			});
		}
	};
}
