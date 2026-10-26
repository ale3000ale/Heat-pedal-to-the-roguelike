import { describe, expect, it } from 'vitest';
import {
	orderAutoScrollStep,
	orderDragClamp,
	orderDragOffset,
	orderDragTarget
} from './draft-order-drag';

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

describe('resa visiva del drag ordine', () => {
	it('mantiene la scheda sotto il puntatore anche dopo il cambio di slot', () => {
		expect(orderDragOffset(centers, 0, 0, 20)).toBe(20);
		expect(orderDragOffset(centers, 0, 1, 60)).toBe(12);
		expect(orderDragOffset(centers, 2, 0, -100)).toBe(-4);
		expect(() => orderDragOffset(centers, 0, 3, 10)).toThrow(RangeError);
	});
	it('scorre solo nelle fasce vicino ai bordi, piu veloce verso l esterno', () => {
		expect(orderAutoScrollStep(300, 0, 600)).toBe(0);
		expect(orderAutoScrollStep(50, 0, 600)).toBeLessThan(0);
		expect(orderAutoScrollStep(-20, 0, 600)).toBe(-14);
		expect(orderAutoScrollStep(590, 0, 600)).toBeGreaterThan(0);
		expect(orderAutoScrollStep(700, 0, 600)).toBe(14);
		expect(Math.abs(orderAutoScrollStep(10, 0, 600))).toBeGreaterThan(
			Math.abs(orderAutoScrollStep(40, 0, 600))
		);
		expect(orderAutoScrollStep(NaN, 0, 600)).toBe(0);
		expect(orderAutoScrollStep(10, 100, 100)).toBe(0);
	});
});

describe('limite del drag ordine', () => {
	const list = { top: 100, bottom: 300 };
	it('tiene la scheda dentro il rettangolo della lista', () => {
		const card = { top: 150, bottom: 190 };
		expect(orderDragClamp(0, list, card)).toBe(0);
		expect(orderDragClamp(-500, list, card)).toBe(-50);
		expect(orderDragClamp(500, list, card)).toBe(110);
		expect(orderDragClamp(30, list, card)).toBe(30);
	});
	it('blocca prima e ultima scheda sui rispettivi bordi', () => {
		expect(orderDragClamp(-20, list, { top: 100, bottom: 140 })).toBe(0);
		expect(orderDragClamp(20, list, { top: 260, bottom: 300 })).toBe(0);
	});
});
