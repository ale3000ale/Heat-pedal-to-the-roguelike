/** Cattura la posizione della griglia nel suo dialog prima di una scrittura.
 * @param anchor Griglia di origine montata; null/undefined e consentito in SSR.
 * @returns Handle monouso restore/cancel, oppure null se non c'e un dialog visibile.
 * restore compensa solo scrollTop del dialog, entro i limiti correnti; non cambia focus,
 * carte o scroll della pagina. cancel rimuove i listener senza correggere lo scroll.
 * Un input utente intervenuto nel dialog impedisce il recupero. Nessun DOM all'import,
 * timer o rete. Le API DOM sono invocate solo quando e fornito un elemento montato.
 */
export function captureDraftDeckScroll(anchor?: HTMLElement | null) {
	const source = anchor;
	if (!source?.isConnected || source.getClientRects().length === 0) return null;
	const scroller = source.closest<HTMLElement>('[role="dialog"]');
	if (!scroller?.isConnected) return null;
	const initialOffset = source.getBoundingClientRect().top - scroller.getBoundingClientRect().top;
	if (!Number.isFinite(initialOffset)) return null;
	let active = true;
	let interrupted = false;
	const events = ['wheel', 'touchstart', 'pointerdown', 'keydown'] as const;
	const interrupt = () => {
		interrupted = true;
	};
	for (const event of events) {
		scroller.addEventListener(event, interrupt, { capture: true, passive: true });
	}

	const cancel = (): void => {
		if (!active) return;
		active = false;
		for (const event of events) scroller.removeEventListener(event, interrupt, true);
	};

	const restore = (): boolean => {
		if (!active) return false;
		try {
			if (
				interrupted ||
				!source.isConnected ||
				!scroller.isConnected ||
				source.getClientRects().length === 0 ||
				source.closest('[role="dialog"]') !== scroller
			)
				return false;
			const offset = source.getBoundingClientRect().top - scroller.getBoundingClientRect().top;
			const target = scroller.scrollTop + offset - initialOffset;
			const maximum = Math.max(0, scroller.scrollHeight - scroller.clientHeight);
			if (!Number.isFinite(target) || !Number.isFinite(maximum)) return false;
			// Usa il delta residuo: non sommare di nuovo un ancoraggio gia fatto dal browser.
			scroller.scrollTop = Math.max(0, Math.min(target, maximum));
			return true;
		} finally {
			cancel();
		}
	};
	return { restore, cancel };
}
