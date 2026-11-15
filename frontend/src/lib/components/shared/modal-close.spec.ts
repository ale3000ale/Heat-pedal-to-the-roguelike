import { describe, expect, it, vi } from 'vitest';
import { shouldCloseModal, type ModalCloseSource } from './modal-close';

const sources: ModalCloseSource[] = ['button', 'escape', 'outside'];

describe('politica di chiusura del modal', () => {
	it.each(sources)('conserva la chiusura predefinita da %s', (source) => {
		expect(shouldCloseModal(source, true)).toBe(true);
	});

	it.each(['escape', 'outside'] as const)('rispetta closeOnOutside falso per %s', (source) => {
		expect(shouldCloseModal(source, false)).toBe(false);
	});

	it('mantiene attiva la X anche con closeOnOutside falso', () => {
		expect(shouldCloseModal('button', false)).toBe(true);
	});

	it.each(sources)('delega %s senza autorizzare una chiusura automatica', (source) => {
		const interceptor = vi.fn();
		expect(shouldCloseModal(source, true, interceptor)).toBe(false);
		expect(interceptor).toHaveBeenCalledTimes(1);
	});

	it.each(['escape', 'outside'] as const)(
		'non invoca l’intercettore per %s disabilitato',
		(source) => {
			const interceptor = vi.fn();
			expect(shouldCloseModal(source, false, interceptor)).toBe(false);
			expect(interceptor).not.toHaveBeenCalled();
		}
	);

	it('non chiude se l’intercettore solleva un errore', () => {
		let open = true;
		const interceptor = () => {
			throw new Error('Chiusura rifiutata');
		};
		expect(() => {
			if (shouldCloseModal('button', true, interceptor)) open = false;
		}).toThrow('Chiusura rifiutata');
		expect(open).toBe(true);
	});
});
