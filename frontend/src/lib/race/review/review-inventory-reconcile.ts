import type { RaceReview } from '../race-review-types';
import type { ReviewInventoryPilot } from './review-counts-types';

type Pilot = ReviewInventoryPilot;
export interface ReviewLocalIssue {
	pilotId: number;
	cardName: string;
	reason: 'pilot_removed' | 'card_removed' | 'out_of_range';
	remaining: number;
	total: number | null;
}

const nameKey = (name: string) => name.trim().toLowerCase();
const copyPilots = (pilots: readonly Pilot[]) =>
	pilots.map((pilot) => ({ ...pilot, cards: pilot.cards.map((card) => ({ ...card })) }));

/**
 * Identifica soltanto una revisione attiva del proprio utente.
 * @param review Stato autorevole letto dal backend.
 * @param userId Utente del contesto corrente.
 * @returns Chiave gara/revisore/inizio, oppure null se non propria o non attiva.
 * Non autorizza richieste e non sostituisce il controllo server della scadenza.
 */
export function ownReviewKey(review: RaceReview, userId: number): string | null {
	if (
		!review.in_review ||
		review.reviewer_user_id !== userId ||
		!review.review_started_at ||
		review.review_closed_at !== null ||
		!Number.isSafeInteger(userId) ||
		userId < 1
	)
		return null;
	return JSON.stringify([review.race_id, userId, review.review_started_at]);
}

/** Rifiuta piloti/carte duplicati e, nelle fonti server, quantita' fuori dai limiti. */
function validate(pilots: readonly Pilot[], checkCounts: boolean): void {
	const ids = new Set<number>();
	for (const pilot of pilots) {
		if (ids.has(pilot.pilot_id)) throw new RangeError('Pilota duplicato');
		ids.add(pilot.pilot_id);
		const names = new Set<string>();
		for (const card of pilot.cards) {
			const key = nameKey(card.card_name);
			if (!key || names.has(key)) throw new RangeError('Carta duplicata o senza nome');
			names.add(key);
			if (
				checkCounts &&
				(!Number.isInteger(card.total) ||
					card.total < 0 ||
					!Number.isInteger(card.remaining) ||
					card.remaining < 0 ||
					card.remaining > card.total)
			)
				throw new RangeError('Snapshot server con conteggi non validi');
		}
	}
}

/** Firma dei dati carte; ignora ordine delle carte e nome visualizzato del pilota. */
function signature(pilot: Pilot | undefined): string {
	return JSON.stringify(
		(pilot?.cards ?? [])
			.map((card) => [
				nameKey(card.card_name),
				card.card_path,
				card.total,
				card.remaining,
				card.gifted,
				card.start,
				card.pool_now,
				card.pool_max
			])
			.sort((a, b) => String(a[0]).localeCompare(String(b[0])))
	);
}

/**
 * Riconcilia conteggi per pilota/carta nella stessa revisione propria.
 * @param base Ultimo inventario/bozza server accettato, non modificato dalla UI.
 * @param local Copia di lavoro corrente, anche se divenuta incompatibile.
 * @param remote Nuovo inventario con bozza server gia' applicata e validata.
 * @returns Copie indipendenti, piloti da ricontrollare, conflitti e blocchi espliciti.
 * @throws RangeError per duplicati o fonti server non valide; mai fallback a [].
 * Il chiamante verifica ownReviewKey prima del merge e gestisce conferme e permessi.
 * Con incompatibilita' restituisce l'intera copia locale, senza clamp o scarti.
 */
export function reconcileReviewInventory(
	base: readonly Pilot[],
	local: readonly Pilot[],
	remote: readonly Pilot[]
) {
	validate(base, true);
	validate(remote, true);
	validate(local, false);
	const baseById = new Map(base.map((pilot) => [pilot.pilot_id, pilot]));
	const remoteById = new Map(remote.map((pilot) => [pilot.pilot_id, pilot]));
	const changedPilotIds = [...new Set([...baseById.keys(), ...remoteById.keys()])].filter(
		(id) =>
			baseById.has(id) !== remoteById.has(id) ||
			signature(baseById.get(id)) !== signature(remoteById.get(id))
	);
	const merged = copyPilots(remote);
	const mergedById = new Map(merged.map((pilot) => [pilot.pilot_id, pilot]));
	const issues: ReviewLocalIssue[] = [];
	const conflicts = new Set<number>();
	for (const pilot of local) {
		const previous = new Map(
			(baseById.get(pilot.pilot_id)?.cards ?? []).map((card) => [nameKey(card.card_name), card])
		);
		const freshPilot = mergedById.get(pilot.pilot_id);
		const freshCards = new Map(
			(freshPilot?.cards ?? []).map((card) => [nameKey(card.card_name), card])
		);
		for (const card of pilot.cards) {
			const before = previous.get(nameKey(card.card_name));
			if (before && Object.is(before.remaining, card.remaining)) continue;
			const fresh = freshCards.get(nameKey(card.card_name));
			let reason: ReviewLocalIssue['reason'] | null = null;
			if (!freshPilot) reason = 'pilot_removed';
			else if (!fresh) reason = 'card_removed';
			else if (
				!Number.isInteger(card.remaining) ||
				card.remaining < 0 ||
				card.remaining > fresh.total
			)
				reason = 'out_of_range';
			if (reason) {
				issues.push({
					pilotId: pilot.pilot_id,
					cardName: card.card_name,
					reason,
					remaining: card.remaining,
					total: fresh?.total ?? null
				});
			} else if (fresh) {
				if ((!before || before.remaining !== fresh.remaining) && card.remaining !== fresh.remaining)
					conflicts.add(pilot.pilot_id);
				fresh.remaining = card.remaining;
			}
		}
	}
	return {
		pilots: issues.length ? copyPilots(local) : merged,
		changedPilotIds,
		conflictingPilotIds: [...conflicts],
		issues,
		blocked: issues.length > 0
	};
}
