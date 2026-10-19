import { api, ApiError } from '$lib/api';
import type { RaceReview } from '$lib/race-review-types';
import type { ReviewCounts, ReviewIncongruity, ReviewInventory } from './review-counts-types';

export class ReviewConflictError extends ApiError {
	constructor(message: string, public incongruities: ReviewIncongruity[]) {
		super(409, message);
		this.name = 'ReviewConflictError';
	}
}

function base(championshipId: number, raceId: number): string {
	return `/championships/${championshipId}/races/${raceId}/review`;
}

export function fetchReviewInventory(championshipId: number, raceId: number): Promise<ReviewInventory> {
	return api<ReviewInventory>(`${base(championshipId, raceId)}/inventory`);
}

export function fetchReviewDraft(championshipId: number, raceId: number): Promise<ReviewCounts | null> {
	return api<ReviewCounts | null>(`${base(championshipId, raceId)}/draft`);
}

export function saveReviewDraft(championshipId: number, raceId: number, data: ReviewCounts): Promise<void> {
	return api<void>(`${base(championshipId, raceId)}/draft`, { method: 'PUT', body: data });
}

function isIssue(value: unknown): value is ReviewIncongruity {
	if (typeof value !== 'object' || value === null) return false;
	const item = value as Record<string, unknown>;
	return typeof item.card_name === 'string' && typeof item.reason === 'string' &&
		typeof item.pool_now === 'number' && typeof item.pool_after === 'number' &&
		(item.pool_max === null || typeof item.pool_max === 'number');
}

/**
 * Conferma i conteggi mantenendo i dettagli strutturati del conflitto.
 * @param championshipId Campionato della gara.
 * @param raceId Gara da revisionare.
 * @param data Conteggi finali di tutti i piloti.
 * @param doFetch Fetch sostituibile nei test.
 * @returns Stato della revisione confermata.
 * @throws ReviewConflictError Per incongruenze; ApiError per altri errori.
 * Il fetch dedicato evita che il servizio API attuale perda detail.incongruities.
 */
export async function confirmReviewCounts(
	championshipId: number, raceId: number, data: ReviewCounts, doFetch: typeof fetch = fetch
): Promise<RaceReview> {
	let response: Response;
	try {
		response = await doFetch(`/api${base(championshipId, raceId)}/counts/confirm`, {
			method: 'POST', credentials: 'same-origin',
			headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
			body: JSON.stringify(data)
		});
	} catch {
		throw new ApiError(0, 'Server non raggiungibile');
	}
	const body: unknown = await response.json().catch(() => null);
	if (!response.ok) {
		const detail = body && typeof body === 'object' && 'detail' in body ? body.detail : null;
		if (response.status === 409 && detail && typeof detail === 'object' &&
			'incongruities' in detail && Array.isArray(detail.incongruities) &&
			detail.incongruities.every(isIssue)) {
			const message = 'message' in detail && typeof detail.message === 'string'
				? detail.message : 'Correggi le incongruenze delle carte';
			throw new ReviewConflictError(message, detail.incongruities);
		}
		throw new ApiError(response.status, typeof detail === 'string' ? detail : `Errore ${response.status}`);
	}
	if (!body || typeof body !== 'object' || !('race_id' in body)) {
		throw new ApiError(response.status, 'Risposta della revisione non valida');
	}
	return body as RaceReview;
}
