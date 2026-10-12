import { describe, expect, it, vi } from 'vitest';
import { submitCardPoll } from './card-poll-form';

describe('submitCardPoll', () => {
	it('non salva se il testo non è valido', async () => {
		const save = vi.fn();
		const result = await submitCardPoll('abc', save);
		expect(result.ok).toBe(false);
		expect(save).not.toHaveBeenCalled();
	});

	it('non salva se il valore è fuori intervallo', async () => {
		const save = vi.fn();
		const result = await submitCardPoll('11', save);
		expect(result.ok).toBe(false);
		expect(save).not.toHaveBeenCalled();
	});

	it('salva il valore valido e mostra quello del server', async () => {
		const save = vi.fn().mockResolvedValue({ seconds: 6 });
		const result = await submitCardPoll(' 5 ', save);
		expect(save).toHaveBeenCalledWith(5);
		expect(result.ok).toBe(true);
		expect(result.message).toBe('Intervallo salvato: 6 secondi');
	});

	it('mostra il messaggio di errore del server', async () => {
		const save = vi.fn().mockRejectedValue(new Error('Solo admin'));
		const result = await submitCardPoll('5', save);
		expect(result.ok).toBe(false);
		expect(result.message).toBe('Solo admin');
	});

	it('usa un messaggio generico se l\'errore non è un Error', async () => {
		const save = vi.fn().mockRejectedValue('boom');
		const result = await submitCardPoll('5', save);
		expect(result.message).toBe('Salvataggio non riuscito');
	});
});
