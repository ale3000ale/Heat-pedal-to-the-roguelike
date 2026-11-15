import { describe, expect, it, vi } from 'vitest';
import { captureDraftDeckScroll } from './draft-deck-scroll';

/** Geometrie simulate: non rappresenta un browser o un ciclo di rendering Svelte. */
function fixture() {
	const layout = { anchorTop: 250, dialogTop: 50, visible: true };
	const listeners = new Map<string, () => void>();
	const scroller = {
		isConnected: true,
		scrollTop: 300,
		scrollHeight: 1000,
		clientHeight: 400,
		getBoundingClientRect: () => ({ top: layout.dialogTop }),
		addEventListener: vi.fn((name: string, listener: () => void) => {
			listeners.set(name, listener);
		}),
		removeEventListener: vi.fn((name: string, listener: () => void) => {
			if (listeners.get(name) === listener) listeners.delete(name);
		})
	};
	const anchor = {
		isConnected: true,
		getClientRects: () => (layout.visible ? [{}] : []),
		getBoundingClientRect: () => ({ top: layout.anchorTop }),
		closest: vi.fn<() => unknown>(() => scroller)
	};
	return {
		layout,
		listeners,
		scroller,
		anchor,
		capture: () => captureDraftDeckScroll(anchor as unknown as HTMLElement)
	};
}

describe('posizione griglia dopo move draft', () => {
	it('compensa il cambiamento di posizione nel dialog e rimuove i listener', () => {
		const env = fixture();
		const captured = env.capture()!;
		env.layout.anchorTop += 100;
		expect(captured.restore()).toBe(true);
		expect(env.scroller.scrollTop).toBe(400);
		expect(env.listeners.size).toBe(0);
		expect(env.scroller.removeEventListener).toHaveBeenCalledTimes(4);
	});

	it('non duplica una compensazione gia applicata dal browser', () => {
		const env = fixture();
		const captured = env.capture()!;
		env.scroller.scrollTop = 400;
		expect(captured.restore()).toBe(true);
		expect(env.scroller.scrollTop).toBe(400);
	});

	it('ignora lo spostamento del dialog nel viewport', () => {
		const env = fixture();
		const captured = env.capture()!;
		env.layout.anchorTop += 40;
		env.layout.dialogTop += 40;
		expect(captured.restore()).toBe(true);
		expect(env.scroller.scrollTop).toBe(300);
	});

	it.each([
		{ top: 1400, expected: 600 },
		{ top: -1000, expected: 0 }
	])('rispetta i limiti del contenuto: $expected', ({ top, expected }) => {
		const env = fixture();
		const captured = env.capture()!;
		env.layout.anchorTop = top;
		expect(captured.restore()).toBe(true);
		expect(env.scroller.scrollTop).toBe(expected);
	});

	it.each(['wheel', 'touchstart', 'pointerdown', 'keydown'])(
		'non sovrascrive una nuova interazione utente: %s',
		(event) => {
			const env = fixture();
			const captured = env.capture()!;
			env.listeners.get(event)?.();
			env.layout.anchorTop += 100;
			expect(captured.restore()).toBe(false);
			expect(env.scroller.scrollTop).toBe(300);
			expect(env.listeners.size).toBe(0);
		}
	);

	it.each(['anchor', 'dialog', 'hidden', 'reparent'] as const)(
		'non corregge un riferimento non piu valido: %s',
		(reason) => {
			const env = fixture();
			const captured = env.capture()!;
			if (reason === 'anchor') env.anchor.isConnected = false;
			if (reason === 'dialog') env.scroller.isConnected = false;
			if (reason === 'hidden') env.layout.visible = false;
			if (reason === 'reparent') env.anchor.closest.mockReturnValue({});
			expect(captured.restore()).toBe(false);
			expect(env.scroller.scrollTop).toBe(300);
			expect(env.listeners.size).toBe(0);
		}
	);

	it('e monouso e permette cleanup senza recupero', () => {
		const env = fixture();
		const captured = env.capture()!;
		captured.cancel();
		captured.cancel();
		env.layout.anchorTop += 100;
		expect(captured.restore()).toBe(false);
		expect(env.scroller.scrollTop).toBe(300);
		expect(env.scroller.removeEventListener).toHaveBeenCalledTimes(4);
		const next = env.capture()!;
		expect(next.restore()).toBe(true);
		expect(next.restore()).toBe(false);
	});

	it('rifiuta riferimenti SSR, nascosti o geometrie invalide', () => {
		expect(captureDraftDeckScroll()).toBeNull();
		expect(captureDraftDeckScroll(null)).toBeNull();
		const env = fixture();
		env.layout.visible = false;
		expect(env.capture()).toBeNull();
		env.layout.visible = true;
		env.layout.anchorTop = Number.NaN;
		expect(env.capture()).toBeNull();
		expect(env.listeners.size).toBe(0);
	});
});
