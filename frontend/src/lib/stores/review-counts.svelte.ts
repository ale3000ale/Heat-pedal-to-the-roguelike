import { api } from '$lib/api';
import { abandonReview, openReview, reopenReview } from '$lib/race-review-api';
import { secondsLeft } from '$lib/race-review-format';
import type { RaceReview } from '$lib/race-review-types';
import {
	confirmReviewCounts,
	fetchReviewDraft,
	fetchReviewInventory,
	ReviewConflictError,
	saveReviewDraft
} from '$lib/review-counts-api';
import { adjustRemaining, toReviewCounts } from '$lib/review-counts';
import { mergeReviewDraft } from '$lib/review-draft';
import type { ReviewIncongruity, ReviewInventoryPilot } from '$lib/review-counts-types';

export class ReviewCountsStore {
	review = $state<RaceReview | null>(null);
	pilots = $state<ReviewInventoryPilot[]>([]);
	checked = $state<number[]>([]);
	index = $state(0);
	remaining = $state(0);
	busy = $state(false);
	error = $state<string | null>(null);
	notice = $state<string | null>(null);
	issues = $state<ReviewIncongruity[]>([]);
	conflictOpen = $state(false);
	private timer: ReturnType<typeof setInterval> | null = null;
	private disposed = false;

	constructor(
		private championshipId: number,
		private raceId: number
	) {}

	get active(): boolean {
		return this.review?.in_review === true && this.remaining > 0;
	}

	get allReviewed(): boolean {
		return this.pilots.length > 0 && this.pilots.every((p) => this.checked.includes(p.pilot_id));
	}

	private get progressKey(): string {
		return `heat:review:${this.championshipId}:${this.raceId}:${this.review?.reviewer_user_id}:${this.review?.review_started_at}`;
	}

	private persist(): void {
		try {
			sessionStorage.setItem(
				this.progressKey,
				JSON.stringify({
					counts: toReviewCounts(this.pilots),
					checked: this.checked
				})
			);
		} catch {
			this.notice = 'Memoria del browser non disponibile: usa Prossimo per salvare sul server.';
		}
	}

	private restore(): void {
		try {
			const raw = sessionStorage.getItem(this.progressKey);
			if (!raw) return;
			const saved = JSON.parse(raw);
			const pilots = mergeReviewDraft(this.pilots, saved.counts);
			const checked = Array.isArray(saved.checked) ? saved.checked : [];
			this.pilots = pilots;
			this.checked = checked.filter(
				(id: unknown) => typeof id === 'number' && pilots.some((p) => p.pilot_id === id)
			);
		} catch {
			this.notice = 'Progresso locale non valido: riprendi dalla bozza del server.';
		}
	}

	/** Esegue un'azione esclusiva; restituisce false e mostra l'errore se fallisce. */
	private async run(action: () => Promise<void>): Promise<boolean> {
		if (this.busy || this.disposed) return false;
		this.busy = true;
		this.error = null;
		try {
			await action();
			return !this.disposed;
		} catch (e) {
			if (!this.disposed) {
				this.error = e instanceof Error ? e.message : 'Errore sconosciuto';
				if (e instanceof ReviewConflictError) {
					this.issues = e.incongruities;
					this.conflictOpen = true;
				}
			}
			return false;
		} finally {
			this.busy = false;
		}
	}

	private stopTimer(): void {
		if (this.timer !== null) clearInterval(this.timer);
		this.timer = null;
	}

	/** Ferma il timer e impedisce aggiornamenti dopo lo smontaggio. */
	dispose(): void {
		this.disposed = true;
		this.stopTimer();
	}

	private startTimer(): void {
		this.stopTimer();
		this.remaining = secondsLeft(this.review?.review_expires_at ?? null);
		if (!this.review?.in_review || this.disposed) return;
		this.timer = setInterval(() => {
			this.remaining = secondsLeft(this.review?.review_expires_at ?? null);
			if (this.remaining === 0 && !this.busy) {
				this.stopTimer();
				void this.refreshStatus();
			}
		}, 1000);
	}

	/** Rilegge lo stato una volta, anche per elaborare la scadenza sul server. */
	async refreshStatus(): Promise<boolean> {
		return this.run(async () => {
			const review = await api<RaceReview>(
				`/championships/${this.championshipId}/races/${this.raceId}/review`
			);
			if (this.disposed) return;
			this.review = review;
			this.startTimer();
			this.notice = review.review_closed_at
				? 'Revisione conclusa dal server.'
				: 'Revisione non attiva: nessuna modifica locale è stata confermata.';
		});
	}

	/** Apre/riprende o riapre la revisione e recupera inventario e bozza. */
	async start(reopen = false): Promise<boolean> {
		return this.run(async () => {
			const review = await (reopen ? reopenReview : openReview)(this.championshipId, this.raceId);
			if (this.disposed) return;
			this.review = review;
			const [inventory, draft] = await Promise.all([
				fetchReviewInventory(this.championshipId, this.raceId),
				fetchReviewDraft(this.championshipId, this.raceId)
			]);
			if (this.disposed) return;
			this.pilots = inventory.pilots;
			this.checked = [];
			try {
				this.pilots = mergeReviewDraft(this.pilots, draft);
				this.restore();
			} catch (e) {
				this.notice = e instanceof Error ? e.message : 'Ricontrolla la bozza';
			}
			this.index = 0;
			this.startTimer();
		});
	}

	/** Corregge una carta e revoca la spunta del pilota modificato. */
	adjust(pilotId: number, cardName: string, delta: -1 | 1): void {
		if (!this.active || this.busy) return;
		const card = this.pilots
			.find((p) => p.pilot_id === pilotId)
			?.cards.find((c) => c.card_name === cardName);
		if (!card) return;
		card.remaining = adjustRemaining(card.remaining, card.total, delta);
		this.checked = this.checked.filter((id) => id !== pilotId);
		this.persist();
	}

	/** Salva tutti i conteggi; completa il pilota corrente solo con Prossimo. */
	async navigate(target: number, complete = false): Promise<boolean> {
		if (!this.active || target < -1 || target >= this.pilots.length) return false;
		return this.run(async () => {
			await saveReviewDraft(this.championshipId, this.raceId, toReviewCounts(this.pilots));
			if (this.disposed) return;
			const pilot = this.pilots[this.index];
			if (complete && pilot && !this.checked.includes(pilot.pilot_id))
				this.checked.push(pilot.pilot_id);
			this.index = target;
			this.persist();
		});
	}

	/** Conferma solo dopo il controllo di tutti i piloti; un 409 apre il popup. */
	async confirm(): Promise<boolean> {
		if (!this.active || !this.allReviewed) return false;
		return this.run(async () => {
			const review = await confirmReviewCounts(
				this.championshipId,
				this.raceId,
				toReviewCounts(this.pilots)
			);
			if (this.disposed) return;
			this.review = review;
			this.stopTimer();
			this.remaining = 0;
			this.notice = 'Revisione confermata.';
		});
	}

	/** Salva la bozza prima di rinunciare, senza applicare le correzioni alle carte. */
	async abandon(): Promise<boolean> {
		if (!this.active) return false;
		return this.run(async () => {
			await saveReviewDraft(this.championshipId, this.raceId, toReviewCounts(this.pilots));
			const review = await abandonReview(this.championshipId, this.raceId);
			if (this.disposed) return;
			this.review = review;
			this.remaining = 0;
			this.stopTimer();
		});
	}
}
