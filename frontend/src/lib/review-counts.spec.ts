import { describe, expect, it, vi } from 'vitest';
import { adjustRemaining } from './review-counts';
import { confirmReviewCounts, ReviewConflictError } from './review-counts-api';

describe('conteggi della revisione', () => {
	it('non supera il totale con +', () => {
		expect(adjustRemaining(2, 2, 1)).toBe(2);
	});
	it('non scende sotto zero con -', () => {
		expect(adjustRemaining(0, 2, -1)).toBe(0);
	});
	it('permette di correggere il consumo', () => {
		expect(adjustRemaining(1, 2, 1)).toBe(2);
		expect(adjustRemaining(1, 2, -1)).toBe(0);
	});
	it('rifiuta conteggi incoerenti', () => {
		expect(() => adjustRemaining(3, 2, 1)).toThrow(RangeError);
	});
	it('conserva i dettagli delle incongruenze', async () => {
		const issue = { card_name: 'Alettone', reason: '8 su 7', pool_now: 5, pool_after: 8, pool_max: 7 };
		const mocked = vi.fn<typeof fetch>().mockResolvedValue(new Response(JSON.stringify({
			detail: { message: 'Correggi', incongruities: [issue] }
		}), { status: 409 }));
		const request = confirmReviewCounts(1, 2, { pilots: [] }, mocked);
		await expect(request).rejects.toBeInstanceOf(ReviewConflictError);
		await expect(request).rejects.toMatchObject({ incongruities: [issue] });
	});
	it('non converte un errore di permesso in incongruenze', async () => {
		const mocked = vi.fn<typeof fetch>().mockResolvedValue(new Response(JSON.stringify({ detail: 'Permesso negato' }), { status: 403 }));
		await expect(confirmReviewCounts(1, 2, { pilots: [] }, mocked)).rejects.toMatchObject({ status: 403, message: 'Permesso negato' });
	});
});
