import { describe, expect, it } from 'vitest';
import { orderDragTarget } from './draft-order-drag';

const centers = [20, 68, 116];

describe('geometria stabile del drag ordine', () => {
	it('ignora piccoli movimenti prima della soglia', () => {
		expect(orderDragTarget([0, 4, 8], 1, 5)).toBe(1);
		expect(orderDragTarget([0, 4, 8], 1, 6)).toBe(2);
	});
	it('sposta in entrambe le direzioni senza usare il DOM gia riordinato', () => {
		expect(orderDragTarget(centers, 0, 25)).toBe(1);
		expect(orderDragTarget(centers, 2, -25)).toBe(1);
		expect(orderDragTarget(centers, 0, 100)).toBe(2);
		expect(orderDragTarget(centers, 2, -100)).toBe(0);
	});
	it('la stessa posizione non fa oscillare l indice dopo un riordino', () => {
		const first = orderDragTarget(centers, 0, 60);
		for (let index = 0; index < 10; index += 1) expect(orderDragTarget(centers, 0, 60)).toBe(first);
		expect(centers).toEqual([20, 68, 116]);
	});
	it('limita il risultato e accetta centri fuori dal viewport', () => {
		expect(orderDragTarget(centers, 1, 10000)).toBe(2);
		expect(orderDragTarget(centers, 1, -10000)).toBe(0);
		expect(orderDragTarget([-100, -40, 20], 0, 65)).toBe(1);
	});
	it('rifiuta geometrie o movimenti non utilizzabili', () => {
		expect(() => orderDragTarget([], 0, 10)).toThrow(RangeError);
		expect(() => orderDragTarget([20, 20], 0, 10)).toThrow(RangeError);
		expect(() => orderDragTarget([40, 20], 0, 10)).toThrow(RangeError);
		expect(() => orderDragTarget(centers, 3, 10)).toThrow(RangeError);
		expect(() => orderDragTarget(centers, 0, NaN)).toThrow(RangeError);
	});
});
