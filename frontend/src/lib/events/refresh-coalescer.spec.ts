import { describe, expect, it, vi } from 'vitest';
import { createRefreshCoalescer } from './refresh-coalescer';

function deferred<T>() {
	let resolve!: (value: T) => void;
	let reject!: (error: unknown) => void;
	const promise = new Promise<T>((yes, no) => {
		resolve = yes;
		reject = no;
	});
	return { promise, resolve, reject };
}

describe('riletture accorpate', () => {
	it('accorpa invalidazioni e applica solo il risultato non superato', async () => {
		const first = deferred<number>();
		const load = vi.fn().mockReturnValueOnce(first.promise).mockResolvedValue(2);
		const apply = vi.fn();
		const refresh = createRefreshCoalescer({ load, apply, onError: vi.fn() });
		const work = refresh.request();
		void refresh.request();
		void refresh.request();
		expect(load).toHaveBeenCalledOnce();
		first.resolve(1);
		await work;
		expect(load).toHaveBeenCalledTimes(2);
		expect(apply).toHaveBeenCalledExactlyOnceWith(2);
	});

	it('non applica risultati ne errori dopo dispose e cancella la coda', async () => {
		const first = deferred<number>();
		const load = vi.fn(() => first.promise);
		const apply = vi.fn();
		const onError = vi.fn();
		const refresh = createRefreshCoalescer({ load, apply, onError });
		const work = refresh.request();
		void refresh.request();
		refresh.dispose();
		first.resolve(1);
		await work;
		await refresh.request();
		expect(load).toHaveBeenCalledOnce();
		expect(apply).not.toHaveBeenCalled();
		expect(onError).not.toHaveBeenCalled();
	});

	it('rende osservabile un errore e permette il tentativo successivo', async () => {
		const error = new Error('rete');
		const load = vi.fn().mockRejectedValueOnce(error).mockResolvedValue(3);
		const apply = vi.fn();
		const onError = vi.fn();
		const refresh = createRefreshCoalescer({ load, apply, onError });
		await refresh.request();
		expect(onError).toHaveBeenCalledExactlyOnceWith(error);
		await refresh.request();
		expect(apply).toHaveBeenCalledExactlyOnceWith(3);
	});
});
