import { afterEach, describe, expect, it, vi } from 'vitest';
import { draftHostFocus } from './draft-host-focus';

/** DOM minimo simulato: verifica chiamate focus e lifecycle, non layout o scroll reale. */
function environment() {
	const tasks: (() => void)[] = [];
	const windowListeners = new Map<string, (event: unknown) => void>();
	let activeElement: FakeElement | null = null;

	class FakeElement {
		isConnected = true;
		tabIndex = 0;
		disabled = false;
		inert = false;
		visible = true;
		children: FakeElement[] = [];
		listeners = new Map<string, (event: unknown) => void>();
		focus = vi.fn<(options?: FocusOptions) => void>(() => {
			activeElement = this;
		});
		contains(target: unknown): boolean {
			return target === this || this.children.some((child) => child.contains(target));
		}
		querySelectorAll(): FakeElement[] {
			return this.children;
		}
		matches(): boolean {
			return this.disabled;
		}
		closest(): FakeElement | null {
			return this.inert ? this : null;
		}
		getClientRects(): object[] {
			return this.visible ? [{}] : [];
		}
		addEventListener(name: string, listener: (event: unknown) => void): void {
			this.listeners.set(name, listener);
		}
		removeEventListener(name: string, listener: (event: unknown) => void): void {
			if (this.listeners.get(name) === listener) this.listeners.delete(name);
		}
	}

	const previous = new FakeElement();
	const body = new FakeElement();
	const node = new FakeElement();
	const first = new FakeElement();
	const last = new FakeElement();
	node.tabIndex = -1;
	node.children = [first, last];
	activeElement = previous;
	vi.stubGlobal('Node', FakeElement);
	vi.stubGlobal('HTMLElement', FakeElement);
	vi.stubGlobal('document', {
		get activeElement() {
			return activeElement;
		},
		body
	});
	vi.stubGlobal('window', {
		addEventListener(name: string, listener: (event: unknown) => void) {
			windowListeners.set(name, listener);
		},
		removeEventListener(name: string, listener: (event: unknown) => void) {
			if (windowListeners.get(name) === listener) windowListeners.delete(name);
		}
	});
	vi.stubGlobal('queueMicrotask', (task: () => void) => tasks.push(task));
	return {
		node,
		first,
		last,
		previous,
		windowListeners,
		start: () => draftHostFocus(node as unknown as HTMLElement),
		createElement: () => new FakeElement(),
		setActive(element: FakeElement | null) {
			activeElement = element;
		},
		focusIn(target: unknown) {
			windowListeners.get('focusin')?.({ target });
		},
		key(event: unknown) {
			node.listeners.get('keydown')?.(event);
		},
		flush() {
			while (tasks.length > 0) tasks.shift()?.();
		}
	};
}

afterEach(() => vi.unstubAllGlobals());

describe('focus automatico del flusso draft', () => {
	it('richiede preventScroll all ingresso e al recupero del focus esterno', () => {
		const env = environment();
		const action = env.start();
		env.flush();
		expect(env.first.focus).toHaveBeenLastCalledWith({ preventScroll: true });
		const outside = env.createElement();
		env.setActive(outside);
		env.focusIn(outside);
		expect(env.first.focus).toHaveBeenCalledTimes(2);
		expect(env.first.focus).toHaveBeenLastCalledWith({ preventScroll: true });
		env.focusIn(env.last);
		expect(env.first.focus).toHaveBeenCalledTimes(2);
		action.destroy();
		env.flush();
	});

	it('usa preventScroll anche sul contenitore se non ci sono controlli', () => {
		const env = environment();
		env.node.children = [];
		const action = env.start();
		env.flush();
		expect(env.node.focus).toHaveBeenLastCalledWith({ preventScroll: true });
		action.destroy();
		env.flush();
	});

	it('mantiene lo scroll normale per Tab e Shift Tab ai bordi', () => {
		const env = environment();
		const action = env.start();
		env.flush();
		env.first.focus.mockClear();
		env.setActive(env.last);
		const forward = { key: 'Tab', shiftKey: false, preventDefault: vi.fn() };
		env.key(forward);
		expect(forward.preventDefault).toHaveBeenCalledOnce();
		expect(env.first.focus).toHaveBeenLastCalledWith();
		const backward = { key: 'Tab', shiftKey: true, preventDefault: vi.fn() };
		env.key(backward);
		expect(backward.preventDefault).toHaveBeenCalledOnce();
		expect(env.last.focus).toHaveBeenLastCalledWith();
		action.destroy();
		env.flush();
	});

	it('ripristina il focus precedente senza scroll e rimuove i listener', () => {
		const env = environment();
		const action = env.start();
		env.flush();
		action.destroy();
		expect(env.node.listeners.size).toBe(0);
		expect(env.windowListeners.size).toBe(0);
		env.flush();
		expect(env.previous.focus).toHaveBeenCalledWith({ preventScroll: true });
	});

	it('non sottrae il focus a un altro flusso dopo destroy', () => {
		const env = environment();
		const action = env.start();
		env.flush();
		action.destroy();
		const nextFlow = env.createElement();
		env.setActive(nextFlow);
		env.flush();
		expect(env.previous.focus).not.toHaveBeenCalled();
	});

	it('ignora autofocus pendente dopo distruzione o disconnessione', () => {
		const env = environment();
		const action = env.start();
		action.destroy();
		env.flush();
		expect(env.first.focus).not.toHaveBeenCalled();
		const disconnected = environment();
		disconnected.node.isConnected = false;
		const other = disconnected.start();
		disconnected.flush();
		expect(disconnected.first.focus).not.toHaveBeenCalled();
		other.destroy();
		disconnected.flush();
	});
});
