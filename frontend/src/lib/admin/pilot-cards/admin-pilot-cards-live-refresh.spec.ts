import { describe, expect, it, vi } from 'vitest';
import { createAdminCardLiveRefresh } from './admin-pilot-cards-live-refresh';

function deferred<T>() {
	let resolve!: (value: T) => void;
	let reject!: (error: unknown) => void;
	const promise = new Promise<T>((yes, no) => {
		resolve = yes;
		reject = no;
	});
	return { promise, resolve, reject };
}

async function flush() {
	for (let index = 0; index < 20; index += 1) await Promise.resolve();
}

function harness() {
	const state = { busy: false, preserve: false };
	const reads: ReturnType<typeof deferred<number>>[] = [];
	const applied: number[] = [];
	const errors: unknown[] = [];
	let active = 0;
	let maximum = 0;
	const load = vi.fn(() => {
		const read = deferred<number>();
		reads.push(read);
		active += 1;
		maximum = Math.max(maximum, active);
		return read.promise.finally(() => {
			active -= 1;
		});
	});
	const apply = vi.fn((value: number) => {
		applied.push(value);
	});
	const onError = vi.fn((error: unknown) => {
		errors.push(error);
	});
	const onStale = vi.fn();
	const live = createAdminCardLiveRefresh({ load, apply, onError, onStale, getState: () => state });
	return {
		state,
		reads,
		applied,
		errors,
		load,
		apply,
		onError,
		onStale,
		live,
		maximum: () => maximum
	};
}

describe('riletture live admin protette', () => {
	it('non legge implicitamente alla costruzione', () => {
		const h = harness();
		expect(h.load).not.toHaveBeenCalled();
		h.live.dispose();
	});

	it('accorpa invalidazioni e scarta il risultato vecchio senza sovrapporre GET', async () => {
		const h = harness();
		const done = h.live.invalidate();
		void h.live.invalidate();
		void h.live.invalidate();
		expect(h.reads).toHaveLength(1);
		h.reads[0].resolve(1);
		await flush();
		expect(h.reads).toHaveLength(2);
		expect(h.applied).toEqual([]);
		h.reads[1].resolve(2);
		await done;
		expect(h.applied).toEqual([2]);
		expect(h.maximum()).toBe(1);
		h.live.dispose();
	});

	it('preserva la bozza e non sblocca le riletture per semplice reset locale', async () => {
		const h = harness();
		h.state.preserve = true;
		await h.live.invalidate();
		await h.live.invalidate();
		expect(h.load).not.toHaveBeenCalled();
		expect(h.onStale).toHaveBeenCalledTimes(1);
		h.state.preserve = false;
		h.live.stateChanged();
		await flush();
		expect(h.load).not.toHaveBeenCalled();
		h.live.acceptServerSnapshot();
		expect(h.reads).toHaveLength(1);
		h.reads[0].resolve(3);
		await flush();
		expect(h.applied).toEqual([3]);
		h.live.dispose();
	});

	it('rinvia i segnali durante una richiesta e legge dopo il rilascio', async () => {
		const h = harness();
		h.state.busy = true;
		await h.live.invalidate();
		expect(h.load).not.toHaveBeenCalled();
		h.state.busy = false;
		h.live.stateChanged();
		expect(h.reads).toHaveLength(1);
		h.reads[0].resolve(4);
		await flush();
		expect(h.applied).toEqual([4]);
		h.live.dispose();
	});

	it.each(['value', 'error'])(
		'non applica %s di una GET iniziata prima del busy',
		async (outcome) => {
			const h = harness();
			const done = h.live.invalidate();
			h.state.busy = true;
			h.live.stateChanged();
			if (outcome === 'value') h.reads[0].resolve(1);
			else h.reads[0].reject(new Error('Errore obsoleto'));
			await done;
			expect(h.applied).toEqual([]);
			expect(h.errors).toEqual([]);
			h.state.busy = false;
			h.live.stateChanged();
			expect(h.reads).toHaveLength(2);
			h.reads[1].resolve(5);
			await flush();
			expect(h.applied).toEqual([5]);
			expect(h.maximum()).toBe(1);
			h.live.dispose();
		}
	);

	it('non sovrascrive una bozza creata durante la GET', async () => {
		const h = harness();
		const done = h.live.invalidate();
		h.state.preserve = true;
		h.reads[0].resolve(1);
		await done;
		expect(h.applied).toEqual([]);
		expect(h.onStale).toHaveBeenCalledTimes(1);
		expect(h.load).toHaveBeenCalledTimes(1);
		h.live.dispose();
	});

	it('mostra un errore attuale senza retry automatici', async () => {
		const h = harness();
		const done = h.live.invalidate();
		const failure = new Error('Server non raggiungibile');
		h.reads[0].reject(failure);
		await done;
		await flush();
		expect(h.onError).toHaveBeenCalledExactlyOnceWith(failure);
		expect(h.load).toHaveBeenCalledTimes(1);
		expect(h.applied).toEqual([]);
		h.live.dispose();
	});

	it('non legge durante busy neppure dopo accettazione server e preserva una bozza ancora protetta', async () => {
		const h = harness();
		h.state.busy = true;
		await h.live.invalidate();
		h.live.acceptServerSnapshot();
		expect(h.load).not.toHaveBeenCalled();
		h.state.preserve = true;
		h.state.busy = false;
		h.live.stateChanged();
		expect(h.onStale).toHaveBeenCalledTimes(1);
		expect(h.load).not.toHaveBeenCalled();
		h.live.dispose();
	});

	it('invalida una GET precedente a uno snapshot server accettato esplicitamente', async () => {
		const h = harness();
		const done = h.live.invalidate();
		h.live.acceptServerSnapshot();
		h.reads[0].resolve(1);
		await flush();
		expect(h.applied).toEqual([]);
		expect(h.reads).toHaveLength(2);
		h.reads[1].resolve(6);
		await done;
		expect(h.applied).toEqual([6]);
		h.live.dispose();
	});

	it.each(['value', 'error'])('ignora %s dopo dispose e non riparte', async (outcome) => {
		const h = harness();
		const done = h.live.invalidate();
		h.live.dispose();
		h.live.dispose();
		if (outcome === 'value') h.reads[0].resolve(1);
		else h.reads[0].reject(new Error('Errore tardivo'));
		await done;
		await h.live.invalidate();
		h.live.stateChanged();
		h.live.acceptServerSnapshot();
		expect(h.applied).toEqual([]);
		expect(h.errors).toEqual([]);
		expect(h.load).toHaveBeenCalledTimes(1);
	});

	it('inoltra un errore di applicazione senza ripetere la lettura', async () => {
		const h = harness();
		const failure = new Error('Snapshot non applicabile');
		h.apply.mockImplementationOnce(() => {
			throw failure;
		});
		const done = h.live.invalidate();
		h.reads[0].resolve(1);
		await done;
		expect(h.onError).toHaveBeenCalledExactlyOnceWith(failure);
		expect(h.load).toHaveBeenCalledTimes(1);
		h.live.dispose();
	});

	it('non interferisce con il coordinatore di un altro contesto', async () => {
		const old = harness();
		const current = harness();
		const oldDone = old.live.invalidate();
		const currentDone = current.live.invalidate();
		old.live.dispose();
		old.reads[0].resolve(1);
		current.reads[0].resolve(7);
		await Promise.all([oldDone, currentDone]);
		expect(old.applied).toEqual([]);
		expect(current.applied).toEqual([7]);
		current.live.dispose();
	});
});
