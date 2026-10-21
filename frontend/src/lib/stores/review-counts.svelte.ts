import { SvelteSet } from 'svelte/reactivity';
import { api, ApiError } from '$lib/api';
import { auth } from '$lib/auth.svelte';
import {
	ownReviewKey,
	reconcileReviewInventory,
	type ReviewLocalIssue
} from '$lib/review-inventory-reconcile';
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
import type {
	ReviewCounts,
	ReviewIncongruity,
	ReviewInventoryPilot
} from '$lib/review-counts-types';

import { startLiveRefresh, type LiveRefreshOptions } from '$lib/events/live-refresh.svelte';
import { eventClient } from '$lib/events/event-client';
type Pilot = ReviewInventoryPilot;
interface LiveSnapshot {
	review: RaceReview;
	pilots: Pilot[] | null;
	version: number;
	problem: string | null;
	draftKey: string | null;
	rawDraft: string | null;
}
const copyPilots = (pilots: readonly Pilot[]) =>
	pilots.map((p) => ({ ...p, cards: p.cards.map((c) => ({ ...c })) }));
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
	blocked = $state(false);
	synchronized = $state(true);
	liveError = $state<string | null>(null);
	localIssues = $state<ReviewLocalIssue[]>([]);
	previousPilots = $state<Pilot[]>([]);
	localBackup = $state<string | null>(null);
	serverDraftText = $state<string | null>(null);
	private baseline: Pilot[] | null = null;
	private ignoredDraft: string | null = null;
	private liveVersion = 0;
	private backupNumber = 0;
	private live: { refresh: () => Promise<void>; dispose: () => void } | null = null;
	private stopStatus: () => void = () => undefined;
	private stopAuthEvents: () => void = () => undefined;
	private disposed = false;
	private readonly userId = auth.user?.id ?? 0;
	private sessionKey: string | null = null;
	private progressScope: string | null = null;

	constructor(
		private championshipId: number,
		private raceId: number
	) {}

	get active(): boolean {
		return (
			!this.disposed &&
			this.synchronized &&
			!this.blocked &&
			auth.user?.id === this.userId &&
			this.review !== null &&
			this.sessionKey !== null &&
			ownReviewKey(this.review, this.userId) === this.sessionKey &&
			this.remaining > 0
		);
	}

	get allReviewed(): boolean {
		return this.pilots.length > 0 && this.pilots.every((p) => this.checked.includes(p.pilot_id));
	}

	private get progressKey(): string {
		return (
			this.progressScope ??
			`heat:review:${this.championshipId}:${this.raceId}:${this.review?.reviewer_user_id}:${this.review?.review_started_at}`
		);
	}

	private persist(): void {
		if (!this.progressScope) return;
		try {
			sessionStorage.setItem(
				this.progressKey,
				JSON.stringify({
					counts: toReviewCounts(this.pilots),
					checked: this.checked,
					base: this.baseline
				})
			);
		} catch {
			this.notice = 'Memoria del browser non disponibile: usa Prossimo per salvare sul server.';
		}
	}

	/** Ripristina solo la chiave propria; bozze legacy revocano tutte le spunte. */
	private restore(): void {
		let raw: string | null = null;
		try {
			raw = sessionStorage.getItem(this.progressKey);
			if (!raw) return;
			const saved = JSON.parse(raw) as {
				counts: ReviewCounts;
				checked?: unknown[];
				base?: Pilot[];
			};
			const fresh = this.baseline ?? [];
			const base = saved.base ?? fresh;
			const result = reconcileReviewInventory(base, mergeReviewDraft(base, saved.counts), fresh);
			this.pilots = result.pilots;
			this.blocked = result.blocked;
			this.localIssues = result.issues;
			if (result.blocked) this.baseline = copyPilots(base);
			const changed = new SvelteSet([...result.changedPilotIds, ...result.conflictingPilotIds]);
			this.checked =
				!saved.base || result.blocked
					? []
					: [
							...new SvelteSet(
								(saved.checked ?? []).filter(
									(id): id is number =>
										typeof id === 'number' &&
										!changed.has(id) &&
										this.pilots.some((p) => p.pilot_id === id)
								)
							)
						];
		} catch {
			this.localBackup = raw;
			this.blocked = true;
			this.checked = [];
			this.notice = 'Progresso locale incompatibile conservato: rileggi con conferma.';
		}
	}

	/** Esegue un'azione esclusiva; restituisce false e mostra l'errore se fallisce. */
	private async run(action: () => Promise<void>): Promise<boolean> {
		if (this.busy || this.disposed) return false;
		this.liveVersion += 1;
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
			this.liveVersion += 1;
			if (!this.disposed) void this.live?.refresh();
		}
	}

	get owned(): boolean {
		return (
			auth.user?.id === this.userId &&
			this.review?.in_review === true &&
			this.review.reviewer_user_id === this.userId
		);
	}
	private ensureContext(): void {
		if (this.disposed || auth.user?.id !== this.userId) throw new Error('Contesto terminato');
	}
	private expireLive(): void {
		if (this.disposed) return;
		this.dispose();
		if (auth.user?.id === this.userId) auth.user = null;
	}
	private liveFailed(cause: unknown): void {
		if (this.disposed) return;
		if (cause instanceof ApiError && cause.status === 401) {
			this.expireLive();
			return;
		}
		if (auth.user?.id !== this.userId) {
			this.dispose();
			return;
		}
		this.synchronized = false;
		this.liveError = cause instanceof Error ? cause.message : 'Errore aggiornamento';
	}
	private async readLiveState(): Promise<RaceReview> {
		this.ensureContext();
		const review = await api<RaceReview>(
			`/championships/${this.championshipId}/races/${this.raceId}/review`
		);
		this.ensureContext();
		if (review.race_id !== this.raceId) throw new Error('Risposta di altra gara');
		return review;
	}
	/** Snapshot immutabile; bozza solo propria, chiave verificata prima e dopo le risorse. */
	private async loadLive(): Promise<LiveSnapshot> {
		const version = this.liveVersion;
		const only = (review: RaceReview): LiveSnapshot => ({
			review,
			version,
			pilots: null,
			problem: null,
			draftKey: null,
			rawDraft: null
		});
		const first = await this.readLiveState();
		const key = ownReviewKey(first, this.userId);
		if (!key) return only(first);
		let inventory;
		let draft: ReviewCounts | null;
		try {
			[inventory, draft] = await Promise.all([
				fetchReviewInventory(this.championshipId, this.raceId),
				fetchReviewDraft(this.championshipId, this.raceId)
			]);
		} catch (cause) {
			if (cause instanceof ApiError && (cause.status === 403 || cause.status === 409)) {
				const latest = await this.readLiveState();
				if (ownReviewKey(latest, this.userId) !== key) return only(latest);
			}
			throw cause;
		}
		const review = await this.readLiveState();
		if (ownReviewKey(review, this.userId) !== key) return only(review);
		if (inventory.race_id !== this.raceId) throw new Error('Inventario di altra gara');
		let pilots = inventory.pilots;
		let problem: string | null = null;
		try {
			pilots = mergeReviewDraft(pilots, draft);
		} catch (cause) {
			if (!(cause instanceof RangeError)) throw cause;
			problem = cause.message;
		}
		return {
			review,
			version,
			pilots,
			problem,
			draftKey: JSON.stringify([key, draft]),
			rawDraft: problem ? JSON.stringify(draft) : null
		};
	}
	/** Applica copie e merge nel solo contesto corrente; replace e' solo un recupero esplicito. */
	private applyLive(snapshot: LiveSnapshot, replace = false): void {
		if (this.disposed) return;
		if (!replace && (this.busy || snapshot.version !== this.liveVersion)) {
			if (!this.busy) void this.live?.refresh();
			return;
		}
		this.ensureContext();
		this.review = snapshot.review;
		this.startTimer();
		this.synchronized = true;
		this.liveError = null;
		const key = ownReviewKey(snapshot.review, this.userId);
		if (!key || snapshot.pilots === null) {
			this.checked = [];
			this.blocked = this.pilots.length > 0;
			if (key) this.synchronized = false;
			this.notice = 'Revisione non modificabile: copia locale conservata.';
			return;
		}
		if (!replace && this.sessionKey !== null && this.sessionKey !== key) {
			this.blocked = true;
			this.checked = [];
			this.notice = 'Inizio revisione cambiato: rileggi con conferma.';
			return;
		}
		this.serverDraftText = snapshot.rawDraft;
		if (!replace && snapshot.problem && this.ignoredDraft !== snapshot.draftKey) {
			this.blocked = true;
			this.checked = [];
			this.notice = snapshot.problem;
			return;
		}
		if (!replace && this.blocked) return;
		const fresh = reconcileReviewInventory([], [], snapshot.pilots).pilots;
		if (replace || this.baseline === null) {
			this.sessionKey = key;
			this.progressScope = `heat:review:${this.championshipId}:${this.raceId}:${this.userId}:${snapshot.review.review_started_at}`;
			this.baseline = copyPilots(fresh);
			this.pilots = copyPilots(fresh);
			this.checked = [];
			this.index = 0;
			this.blocked = false;
			this.localIssues = [];
			this.ignoredDraft = snapshot.problem ? snapshot.draftKey : null;
			if (!replace) this.restore();
		} else {
			const selected = this.pilots[this.index]?.pilot_id;
			const result = reconcileReviewInventory(this.baseline, this.pilots, fresh);
			const changed = new SvelteSet([...result.changedPilotIds, ...result.conflictingPilotIds]);
			this.checked = this.checked.filter(
				(id) => !changed.has(id) && result.pilots.some((p) => p.pilot_id === id)
			);
			this.pilots = result.pilots;
			this.blocked = result.blocked;
			this.localIssues = result.issues;
			if (!result.blocked) this.baseline = copyPilots(fresh);
			this.index = this.pilots.findIndex((p) => p.pilot_id === selected);
			if (changed.size) this.notice = 'Dati aggiornati: ricontrolla i piloti senza spunta.';
		}
		if (!snapshot.problem) this.ignoredDraft = null;
		if (!this.blocked) this.persist();
	}
	/** Un solo client condiviso; dispose rimuove sottoscrizioni e timer. Nessuna POST al mount. */
	connect(intervalMs: number, client?: LiveRefreshOptions<LiveSnapshot>['client']): void {
		if (this.disposed || this.live) return;
		const current = client ?? eventClient;
		const filter = { championshipId: this.championshipId, raceId: this.raceId };
		this.synchronized = false;
		this.live = startLiveRefresh<LiveSnapshot>({
			intervalMs,
			client: current,
			filter,
			load: () => this.loadLive(),
			apply: (snapshot) => this.applyLive(snapshot),
			onError: (cause) => this.liveFailed(cause),
			onUnauthorized: () => this.expireLive()
		});
		this.stopAuthEvents = current.subscribe((event) => {
			if (event.type === 'auth.expired') this.expireLive();
		}, filter);
		this.stopStatus = current.subscribeStatus((status) => {
			if (status === 'expired') this.expireLive();
		});
		if (this.disposed) {
			this.live.dispose();
			this.stopAuthEvents();
			this.stopStatus();
		}
	}
	/** Backup persistente prima di sostituzioni; se storage fallisce interrompe l'operazione. */
	private backupLocal(): void {
		const previous = copyPilots(this.pilots);
		let key = `${this.progressKey}:backup:${Date.now()}:${++this.backupNumber}`;
		while (sessionStorage.getItem(key) !== null) key += ':1';
		sessionStorage.setItem(
			key,
			JSON.stringify({
				counts: toReviewCounts(previous),
				checked: this.checked,
				base: this.baseline,
				local: this.localBackup,
				server: this.serverDraftText
			})
		);
		this.previousPilots = previous;
	}
	/** Conferma obbligatoria; backup, nuova lettura e reset spunte senza scritture REST. */
	async reloadInventory(confirmed = false): Promise<boolean> {
		if (!confirmed) return false;
		return this.run(async () => {
			this.backupLocal();
			const snapshot = await this.loadLive();
			if (!snapshot.pilots || !ownReviewKey(snapshot.review, this.userId))
				throw new Error('Revisione non propria o conclusa');
			this.applyLive(snapshot, true);
			this.notice = 'Inventario riletto e spunte azzerate; nessun conteggio confermato.';
		});
	}

	private stopTimer(): void {
		if (this.timer !== null) clearInterval(this.timer);
		this.timer = null;
	}

	/** Ferma il timer e impedisce aggiornamenti dopo lo smontaggio. */
	dispose(): void {
		if (this.disposed) return;
		this.disposed = true;
		this.synchronized = false;
		this.live?.dispose();
		this.stopStatus();
		this.stopAuthEvents();
		this.stopTimer();
	}

	private startTimer(): void {
		this.stopTimer();
		this.remaining = secondsLeft(this.review?.review_expires_at ?? null);
		if (!this.review?.in_review || this.disposed || this.remaining <= 0) return;
		this.timer = setInterval(() => {
			this.remaining = secondsLeft(this.review?.review_expires_at ?? null);
			if (this.remaining === 0 && !this.busy) {
				this.stopTimer();
				void this.refreshStatus();
			}
		}, 1000);
	}

	/** Rilegge lo snapshot senza aprire o salvare revisioni; errori conservano i dati. */
	async refreshStatus(): Promise<boolean> {
		if (this.disposed) return false;
		try {
			if (this.live) await this.live.refresh();
			else this.applyLive(await this.loadLive());
		} catch (cause) {
			this.liveFailed(cause);
		}
		return !this.disposed && this.synchronized;
	}

	/** Apre solo su azione esplicita; sostituire una copia richiede conferma e backup. */
	async start(reopen = false, confirmed = false): Promise<boolean> {
		if ((this.pilots.length || this.localBackup || this.serverDraftText) && !confirmed) {
			this.error = 'Conferma prima di sostituire la copia locale';
			return false;
		}
		return this.run(async () => {
			if (this.pilots.length || this.localBackup || this.serverDraftText) this.backupLocal();
			await (reopen ? reopenReview : openReview)(this.championshipId, this.raceId);
			const snapshot = await this.loadLive();
			if (!snapshot.pilots || !ownReviewKey(snapshot.review, this.userId))
				throw new Error('Revisione non propria');
			if (snapshot.problem && !confirmed) {
				this.review = snapshot.review;
				this.serverDraftText = snapshot.rawDraft;
				this.blocked = true;
				this.startTimer();
				throw new Error(snapshot.problem);
			}
			this.applyLive(snapshot, true);
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

	/**
	 * Controlla utente e chiave prima di ogni scrittura dei conteggi.
	 * @returns Nessun valore se il contesto e' ancora proprio e attivo.
	 * @throws Error per contesto terminato/cambiato; propaga gli errori HTTP.
	 * Non rende atomiche la verifica e la successiva richiesta al backend.
	 */
	private async verifySession(): Promise<void> {
		if (!this.active) throw new Error('Revisione non modificabile');
		const review = await api<RaceReview>(
			`/championships/${this.championshipId}/races/${this.raceId}/review`
		);
		if (this.disposed) throw new Error('Contesto terminato');
		this.review = review;
		this.startTimer();
		if (!this.active) {
			this.checked = [];
			throw new Error('Utente, revisore o revisione cambiati: conteggi non inviati');
		}
	}

	/** Salva tutti i conteggi; completa il pilota corrente solo con Prossimo. */
	async navigate(target: number, complete = false): Promise<boolean> {
		if (!this.active || target < -1 || target >= this.pilots.length) return false;
		return this.run(async () => {
			await this.verifySession();
			const sent = copyPilots(this.pilots);
			await saveReviewDraft(this.championshipId, this.raceId, toReviewCounts(sent));
			if (this.disposed) return;
			this.baseline = sent;
			this.ignoredDraft = null;
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
			await this.verifySession();
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
			await this.verifySession();
			await saveReviewDraft(this.championshipId, this.raceId, toReviewCounts(this.pilots));
			await this.verifySession();
			const review = await abandonReview(this.championshipId, this.raceId);
			if (this.disposed) return;
			this.review = review;
			this.remaining = 0;
			this.stopTimer();
		});
	}
}
