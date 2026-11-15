// Store della revisione delle carte: stato, errori e conto alla rovescia di una gara.
import {
	abandonReview,
	cancelPlay,
	confirmReview,
	fetchCardPlays,
	grantBonus,
	openReview,
	reopenReview,
	removeCard
} from '$lib/race/race-review-api';
import { secondsLeft } from '$lib/race/race-review-format';
import type { CardMove, PilotPlays, RaceReview } from '$lib/race/race-review-types';

export class RaceReviewStore {
	review = $state<RaceReview | null>(null);
	pilots = $state<PilotPlays[]>([]);
	remaining = $state(0);
	busy = $state(false);
	error = $state<string | null>(null);
	notice = $state<string | null>(null);

	private timer: ReturnType<typeof setInterval> | null = null;

	constructor(
		private championshipId: number,
		private raceId: number
	) {}

	/** Vero se la revisione è aperta e non scaduta. */
	get active(): boolean {
		return this.review?.in_review === true && this.remaining > 0;
	}

	/** Vero se la revisione è stata confermata. */
	get confirmed(): boolean {
		return this.review?.review_closed_at != null;
	}

	// Esegue un'azione gestendo occupato ed errore; ritorna il risultato o null se fallisce.
	private async run<T>(action: () => Promise<T>): Promise<T | null> {
		this.busy = true;
		this.error = null;
		this.notice = null;
		try {
			return await action();
		} catch (e) {
			this.error = e instanceof Error ? e.message : 'Errore sconosciuto';
			return null;
		} finally {
			this.busy = false;
		}
	}

	// Applica lo stato ricevuto e fa partire o ferma il conto alla rovescia.
	private apply(review: RaceReview) {
		this.review = review;
		this.stopTimer();
		this.remaining = review.in_review ? secondsLeft(review.review_expires_at) : 0;
		if (review.in_review) {
			this.timer = setInterval(() => {
				this.remaining = secondsLeft(this.review?.review_expires_at ?? null);
				if (this.remaining === 0) this.stopTimer();
			}, 1000);
		}
	}

	/** Ferma il conto alla rovescia: da chiamare allo smontaggio della pagina. */
	stopTimer() {
		if (this.timer) clearInterval(this.timer);
		this.timer = null;
	}

	/** Ricarica il riepilogo delle giocate. */
	async refreshPlays() {
		const data = await this.run(() => fetchCardPlays(this.championshipId, this.raceId));
		if (data) this.pilots = data;
	}

	/** Apre la revisione (o la riprende) e carica le giocate. */
	async open() {
		const review = await this.run(() => openReview(this.championshipId, this.raceId));
		if (!review) return;
		this.apply(review);
		await this.refreshPlays();
	}

	/** Riapre una revisione già confermata (admin, ultima gara) e carica le giocate. */
	async reopen() {
		const review = await this.run(() => reopenReview(this.championshipId, this.raceId));
		if (!review) return;
		this.apply(review);
		await this.refreshPlays();
	}

	/** Rinuncia alla revisione. */
	async abandon() {
		const review = await this.run(() => abandonReview(this.championshipId, this.raceId));
		if (review) this.apply(review);
	}

	/** Conferma la revisione e consuma le carte. */
	async confirm() {
		const review = await this.run(() => confirmReview(this.championshipId, this.raceId));
		if (!review) return;
		this.apply(review);
		this.notice = 'Revisione confermata: le carte giocate sono state consumate.';
		await this.refreshPlays();
	}

	/** Annulla una giocata e aggiorna il riepilogo. */
	async cancel(playId: number) {
		const play = await this.run(() => cancelPlay(this.championshipId, this.raceId, playId));
		if (!play) return;
		this.notice = `Giocata "${play.card_name}" annullata.`;
		await this.refreshPlays();
	}

	/** Dà una carta bonus a un pilota. Ritorna true se riuscito. */
	async bonus(pilotId: number, cardName: string): Promise<boolean> {
		const move = await this.run(() =>
			grantBonus(this.championshipId, this.raceId, pilotId, cardName)
		);
		return this.report(move, 'Bonus assegnato');
	}

	/** Toglie una carta a un pilota. Ritorna true se riuscito. */
	async remove(pilotId: number, cardName: string): Promise<boolean> {
		const move = await this.run(() =>
			removeCard(this.championshipId, this.raceId, pilotId, cardName)
		);
		return this.report(move, 'Carta rimossa');
	}

	// Imposta il messaggio di esito di bonus e rimozione.
	private report(move: CardMove | null, text: string): boolean {
		if (!move) return false;
		this.notice = `${text}: ${move.card_name}.`;
		return true;
	}
}
