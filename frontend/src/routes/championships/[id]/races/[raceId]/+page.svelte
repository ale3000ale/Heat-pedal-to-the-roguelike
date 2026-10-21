<script lang="ts">
	import { page } from '$app/state';
	import { beforeNavigate, goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { api, ApiError } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import { raceStatusView } from '$lib/race-status';
	import { loadPollIntervalMs } from '$lib/card-poll.svelte';
	import { startLiveRefresh } from '$lib/events/live-refresh.svelte';
	import { hasResultChanges, reconcileResults } from '$lib/race-result-reconcile';
	import type { ResultForm, ResultRow } from '$lib/race-result-reconcile';
	import type { ChampionshipDetail, Pilot } from '$lib/types';
	import type { RaceDetail } from '$lib/race-types';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import PilotGiftButton from '$lib/components/pilot-gift-button.svelte';
	import RaceReviewPanel from '$lib/components/race-review-panel.svelte';

	interface Snapshot {
		race: RaceDetail;
		championship: ChampionshipDetail;
		pilots: Pilot[];
	}

	const MAX_PARTICIPANTS = 12;
	const inputClass =
		'h-8 w-20 rounded-md border border-input bg-background px-2 text-sm disabled:opacity-50';
	let race = $state<RaceDetail | null>(null);
	let championship = $state<ChampionshipDetail | null>(null);
	let myPilots = $state<Pilot[]>([]);
	let order = $state<ResultRow[]>([]);
	let absent = $state<ResultForm['absent']>([]);
	let base = $state<ResultForm | null>(null);
	let context = $state<{ championshipId: number; raceId: number; userId: number } | null>(null);
	let error = $state<string | null>(null);
	let liveError = $state<string | null>(null);
	let saveError = $state<string | null>(null);
	let conflict = $state(false);
	let saved = $state(false);
	let busy = $state(false);
	let leaveTarget = $state<URL | null>(null);
	let allowLeave = false;
	let epoch = 0;
	let live: { refresh: () => Promise<void>; dispose: () => void } | null = null;

	let dirty = $derived(base !== null && hasResultChanges(base, { order, absent }));
	let myIds = $derived(new Set(myPilots.map((p) => p.id)));
	let isRaceClosed = $derived(race !== null && race.participants > 0);
	let canEdit = $derived(
		championship !== null &&
			!championship.is_closed &&
			auth.canManageRaces &&
			(!isRaceClosed || auth.canCorrectRaces)
	);
	let canGift = $derived(
		championship !== null && !championship.is_closed && auth.canManageRaces && !isRaceClosed
	);
	let canReview = $derived(
		championship !== null &&
			!championship.is_closed &&
			auth.canManageRaces &&
			race !== null &&
			(race.status === 'in_review' ||
				(auth.canCorrectRaces &&
					race.is_last &&
					(race.status === 'to_review' || race.status === 'closed')))
	);
	let available = $derived(
		race
			? race.results.filter(
					(r) =>
						!order.some((row) => row.pilot_id === r.pilot_id) &&
						!absent.some((a) => a.pilot_id === r.pilot_id)
				)
			: []
	);
	// La callback legge un Set sempre definito, non la variabile nullable race.
	let knownPilotIds = $derived(new Set(race?.results.map((r) => r.pilot_id) ?? []));
	let unknownPilot = $derived(
		race !== null && [...order, ...absent].some((row) => !knownPilotIds.has(row.pilot_id))
	);
	let canFinish = $derived(
		order.length > 0 && order.length <= MAX_PARTICIPANTS && available.length === 0 && !unknownPilot
	);

	function raceDate(value: string | null): string {
		return value ? new Date(value).toLocaleDateString('it-IT') : 'Data da definire';
	}

	/** Converte la REST in un modulo indipendente; assenti solo con risultati registrati. */
	function fromRace(detail: RaceDetail): ResultForm {
		return {
			order: detail.results
				.filter((r) => r.position !== null)
				.sort((a, b) => (a.position ?? 0) - (b.position ?? 0))
				.map((r) => ({ pilot_id: r.pilot_id, name: r.pilot_name, sponsor: r.sponsor_points })),
			absent:
				detail.participants > 0
					? detail.results
							.filter((r) => r.position === null)
							.map((r) => ({ pilot_id: r.pilot_id, name: r.pilot_name }))
					: []
		};
	}

	/** Copia il modulo senza structuredClone, che non accetta i proxy reattivi Svelte. */
	function copyForm(): ResultForm {
		return { order: order.map((r) => ({ ...r })), absent: absent.map((r) => ({ ...r })) };
	}

	/**
	 * Applica solo letture del contesto corrente e non sovrascrive una PUT in corso.
	 * @param snapshot REST complete, senza effetti UI durante load.
	 * @param version Generazione del contesto campionato/gara/utente.
	 * @returns Nessun valore; aggiorna metadati e campi non modificati.
	 * @throws RangeError dal merge per assegnazioni duplicate; gestito dal coordinatore.
	 */
	function applySnapshot(snapshot: Snapshot, version: number): void {
		if (version !== epoch || busy) return;
		const fresh = fromRace(snapshot.race);
		const merged = base ? reconcileResults(base, { order, absent }, fresh) : null;
		order = merged ? merged.form.order : fresh.order;
		absent = merged ? merged.form.absent : fresh.absent;
		base = fresh;
		race = snapshot.race;
		championship = snapshot.championship;
		myPilots = snapshot.pilots;
		conflict = merged?.hasChanges ? conflict || merged.conflict : false;
		if (merged?.hasChanges) saved = false;
		error = null;
		liveError = null;
	}

	/** Rilettura accorpata, usata anche dalle transizioni del pannello senza reload browser. */
	async function reload(): Promise<void> {
		await live?.refresh();
	}

	$effect(() => {
		const championshipId = Number(page.params.id);
		const raceId = Number(page.params.raceId);
		const userId = auth.user?.id;
		const version = ++epoch;
		race = null;
		championship = null;
		myPilots = [];
		order = [];
		absent = [];
		base = null;
		context = null;
		error = null;
		liveError = null;
		saveError = null;
		conflict = false;
		saved = false;
		busy = false;
		leaveTarget = null;
		allowLeave = false;
		if (!userId) return;
		if (![championshipId, raceId].every((id) => Number.isSafeInteger(id) && id > 0)) {
			error = 'Campionato o gara non validi';
			return;
		}
		context = { championshipId, raceId, userId };
		let cancelled = false;
		let active: { refresh: () => Promise<void>; dispose: () => void } | null = null;
		void loadPollIntervalMs().then((intervalMs) => {
			if (cancelled) return;
			active = startLiveRefresh<Snapshot>({
				intervalMs,
				filter: { championshipId },
				load: async () => {
					const [detail, championshipDetail, pilots] = await Promise.all([
						api<RaceDetail>(`/championships/${championshipId}/races/${raceId}`),
						api<ChampionshipDetail>(`/championships/${championshipId}`),
						api<Pilot[]>('/pilots')
					]);
					return { race: detail, championship: championshipDetail, pilots };
				},
				apply: (snapshot) => applySnapshot(snapshot, version),
				onError: (cause) => {
					if (version !== epoch) return;
					const message = cause instanceof Error ? cause.message : 'Errore sconosciuto';
					if (race) liveError = message;
					else error = message;
				},
				onUnauthorized: () => {
					if (version === epoch) auth.user = null;
				}
			});
			live = active;
		});
		return () => {
			cancelled = true;
			active?.dispose();
			if (live === active) live = null;
			if (epoch === version) epoch += 1;
		};
	});

	function addToOrder(pilotId: number) {
		if (!canEdit || order.length >= MAX_PARTICIPANTS) return;
		if ([...order, ...absent].some((r) => r.pilot_id === pilotId)) return;
		const found = race?.results.find((r) => r.pilot_id === pilotId);
		if (found) order.push({ pilot_id: pilotId, name: found.pilot_name, sponsor: 0 });
	}
	function addToAbsent(pilotId: number) {
		if (!canEdit || [...order, ...absent].some((r) => r.pilot_id === pilotId)) return;
		const found = race?.results.find((r) => r.pilot_id === pilotId);
		if (found) absent.push({ pilot_id: pilotId, name: found.pilot_name });
	}
	function removeFromOrder(index: number) {
		if (canEdit) order.splice(index, 1);
	}
	function removeFromAbsent(index: number) {
		if (canEdit) absent.splice(index, 1);
	}
	function move(index: number, delta: -1 | 1) {
		const target = index + delta;
		if (!canEdit || target < 0 || target >= order.length) return;
		const [row] = order.splice(index, 1);
		order.splice(target, 0, row);
	}
	function cleanSponsor(value: unknown): number {
		const n = Math.trunc(Number(value));
		return Number.isFinite(n) && n > 0 ? n : 0;
	}

	/**
	 * Salva su richiesta esplicita e riconcilia modifiche fatte durante la PUT.
	 * @param event Submit del modulo risultati.
	 * @returns Attende PUT e rilettura; errori mostrati senza cancellare la bozza.
	 * Payload normalizzato come prima; il backend resta autorevole su regole e permessi.
	 */
	async function save(event: SubmitEvent): Promise<void> {
		event.preventDefault();
		if (busy || !canEdit || !canFinish || !context || !race) return;
		const version = epoch;
		const target = context;
		const submitted = copyForm();
		saveError = null;
		saved = false;
		busy = true;
		try {
			hasResultChanges(submitted, submitted);
			const known = new Set(race.results.map((r) => r.pilot_id));
			const assigned = [...submitted.order, ...submitted.absent].map((r) => r.pilot_id);
			if (assigned.length !== known.size || assigned.some((id) => !known.has(id))) {
				throw new RangeError('Ricontrolla tutti i piloti prima di salvare');
			}
			const updated = await api<RaceDetail>(
				`/championships/${target.championshipId}/races/${target.raceId}/results`,
				{
					method: 'PUT',
					body: {
						results: submitted.order.map((r) => ({
							pilot_id: r.pilot_id,
							sponsor_points: cleanSponsor(r.sponsor)
						})),
						absent: submitted.absent.map((r) => r.pilot_id)
					}
				}
			);
			if (version !== epoch) return;
			const fresh = fromRace(updated);
			const merged = reconcileResults(submitted, { order, absent }, fresh);
			order = merged.form.order;
			absent = merged.form.absent;
			base = fresh;
			race = updated;
			conflict = merged.conflict;
			saved = !merged.hasChanges;
		} catch (cause) {
			if (version !== epoch) return;
			if (cause instanceof ApiError && cause.status === 401) auth.user = null;
			else saveError = cause instanceof Error ? cause.message : 'Errore sconosciuto';
		} finally {
			if (version === epoch) {
				busy = false;
				await reload();
			}
		}
	}

	beforeNavigate(({ cancel, to, willUnload }) => {
		if (!auth.user || allowLeave || (!dirty && !busy)) return;
		cancel();
		if (!willUnload && to) leaveTarget = to.url;
	});
	async function confirmLeave() {
		const target = leaveTarget;
		leaveTarget = null;
		if (!target) return;
		allowLeave = true;
		try {
			// eslint-disable-next-line svelte/no-navigation-without-resolve
			await goto(target.pathname + target.search + target.hash);
		} finally {
			allowLeave = false;
		}
	}
</script>

<svelte:head><title>{race ? `Gara ${race.number}` : 'Gara'} - Heat</title></svelte:head>
<main class="mx-auto max-w-5xl space-y-6 p-6">
	<a
		href={resolve('/championships/[id]', { id: page.params.id ?? '' })}
		class="text-sm text-muted-foreground hover:text-foreground">← Campionato</a
	>
	{#if liveError}<p class="text-sm text-destructive" role="alert">
			Aggiornamento non riuscito: {liveError}
		</p>{/if}
	{#if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{:else if !race}
		<p class="text-muted-foreground">Caricamento…</p>
	{:else}
		<div>
			<h1 class="text-2xl font-bold">Gara {race.number}</h1>
			<p class="text-sm text-muted-foreground">
				{raceDate(race.date)} · {race.participants}
				{race.participants === 1 ? 'partecipante' : 'partecipanti'} ·
				<span class={`font-medium ${raceStatusView(race.status).class}`}
					>{raceStatusView(race.status).label}</span
				>
			</p>
		</div>
		{#if conflict && dirty}<p class="text-sm text-destructive" role="alert">
				Sono arrivati risultati diversi dal server. Le modifiche locali sono conservate:
				ricontrollale prima di salvare.
			</p>{/if}
		{#if unknownPilot}<p class="text-sm text-destructive" role="alert">
				La bozza contiene un pilota non più presente nei risultati correnti. Il salvataggio è
				bloccato.
			</p>{/if}
		{#if !canEdit && dirty}
			<Card.Root>
				<Card.Header
					><Card.Title>Bozza locale non salvata</Card.Title><Card.Description
						>Lo stato corrente non consente modifiche. Questa copia resta in sola lettura fino
						all'uscita dalla pagina.</Card.Description
					></Card.Header
				>
				<Card.Content>
					<ol class="list-decimal pl-5">
						{#each order as row (row.pilot_id)}<li>
								{row.name}: {row.sponsor ?? 'vuoto'} sponsor
							</li>{/each}
					</ol>
					<p class="mt-2 text-sm">
						Non partecipano: {absent.map((r) => r.name).join(', ') || 'nessuno'}
					</p>
				</Card.Content>
			</Card.Root>
		{/if}
		{#if isRaceClosed || !canEdit}
			<Card.Root>
				<Card.Header
					><Card.Title>Risultati</Card.Title><Card.Description
						>Chi non ha partecipato ha 0 punti.</Card.Description
					></Card.Header
				>
				<Card.Content>
					{#if !isRaceClosed}<p class="text-sm text-muted-foreground">
							Gara in corso: nessun risultato registrato.
						</p>
					{:else}<ol class="divide-y">
							{#each race.results as result (result.pilot_id)}
								<li class="flex items-center gap-3 py-2">
									<span class="w-6 text-right text-sm text-muted-foreground"
										>{result.position ?? '–'}</span
									>
									<span class="flex-1 font-medium"
										>{result.pilot_name}{#if myIds.has(result.pilot_id)}<span
												class="ml-2 text-xs text-muted-foreground">(tuo)</span
											>{/if}</span
									>
									<span class="text-xs text-muted-foreground">{result.sponsor_points} sponsor</span
									><span class="w-20 text-right text-sm">{result.points} punti</span>
								</li>
							{/each}
						</ol>{/if}
				</Card.Content>
			</Card.Root>
		{/if}
		{#if canReview && context}
			{#key `${context.championshipId}:${context.raceId}:${context.userId}:${race.status}`}
				<RaceReviewPanel
					championshipId={context.championshipId}
					raceId={context.raceId}
					autoOpen={race.status === 'in_review'}
					canOpen={auth.canCorrectRaces && race.is_last}
					reopen={race.status === 'closed'}
					onchanged={reload}
				/>
			{/key}
		{/if}
		{#if canGift && context}
			<Card.Root>
				<Card.Header
					><Card.Title>Piloti iscritti</Card.Title><Card.Description
						>Con il tasto S assegni una carta sponsor casuale al pilota. La carta la vede solo lui.</Card.Description
					></Card.Header
				>
				<Card.Content class="space-y-2"
					>{#each race.results as result (result.pilot_id)}<PilotGiftButton
							championshipId={context.championshipId}
							pilot={{ id: result.pilot_id, name: result.pilot_name }}
						/>{/each}</Card.Content
				>
			</Card.Root>
		{/if}
		{#if canEdit}
			<Card.Root>
				<Card.Header
					><Card.Title>{isRaceClosed ? 'Correggi i risultati' : 'Termina la gara'}</Card.Title
					><Card.Description
						>Metti in classifica i piloti in ordine di arrivo (massimo {MAX_PARTICIPANTS}) con i
						punti sponsor di ciascuno, e indica a mano chi non partecipa. Ogni iscritto va
						assegnato. Gli sponsor vengono assegnati al salvataggio.</Card.Description
					></Card.Header
				>
				<Card.Content class="space-y-4">
					<form onsubmit={save} class="space-y-4">
						<h2 class="text-sm font-semibold">Classifica</h2>
						{#if order.length === 0}<p class="text-sm text-muted-foreground">
								Aggiungi i piloti che hanno partecipato.
							</p>
						{:else}<ol class="divide-y">
								{#each order as row, index (row.pilot_id)}
									<li class="flex flex-wrap items-center gap-2 py-2">
										<span class="w-6 text-right text-sm text-muted-foreground">{index + 1}</span
										><span class="min-w-32 flex-1 font-medium">{row.name}</span>
										<label class="flex items-center gap-1 text-sm text-muted-foreground"
											>Sponsor<input
												type="number"
												min="0"
												step="1"
												class={inputClass}
												bind:value={row.sponsor}
												aria-label={`Punti sponsor di ${row.name}`}
											/></label
										>
										<Button
											type="button"
											size="sm"
											variant="outline"
											disabled={index === 0}
											onclick={() => move(index, -1)}
											aria-label={`Sposta su ${row.name}`}>↑</Button
										>
										<Button
											type="button"
											size="sm"
											variant="outline"
											disabled={index === order.length - 1}
											onclick={() => move(index, 1)}
											aria-label={`Sposta giù ${row.name}`}>↓</Button
										>
										<Button
											type="button"
											size="sm"
											variant="ghost"
											onclick={() => removeFromOrder(index)}
											aria-label={`Togli ${row.name}`}>Togli</Button
										>
									</li>
								{/each}
							</ol>{/if}
						{#if available.length > 0}<div class="space-y-2">
								<h2 class="text-sm font-semibold">Da assegnare</h2>
								{#each available as pilot (pilot.pilot_id)}
									<div class="flex flex-wrap items-center gap-2">
										<span class="min-w-32 flex-1 text-sm font-medium">{pilot.pilot_name}</span>
										<Button
											type="button"
											size="sm"
											variant="secondary"
											disabled={order.length >= MAX_PARTICIPANTS}
											onclick={() => addToOrder(pilot.pilot_id)}>In classifica</Button
										>
										<Button
											type="button"
											size="sm"
											variant="outline"
											onclick={() => addToAbsent(pilot.pilot_id)}
											aria-label={`${pilot.pilot_name} non partecipa`}>Non partecipa</Button
										>
									</div>
								{/each}
							</div>{/if}
						{#if absent.length > 0}<div class="space-y-2">
								<h2 class="text-sm font-semibold">Non partecipano</h2>
								{#each absent as a, index (a.pilot_id)}
									<div class="flex flex-wrap items-center gap-2">
										<span class="min-w-32 flex-1 text-sm font-medium">{a.name}</span><Button
											type="button"
											size="sm"
											variant="ghost"
											onclick={() => removeFromAbsent(index)}
											aria-label={`Rimetti ${a.name} da assegnare`}>Rimetti</Button
										>
									</div>
								{/each}
							</div>{/if}
						<div class="flex flex-wrap items-center gap-3">
							<Button type="submit" disabled={busy || !canFinish}
								>{isRaceClosed ? 'Salva la correzione' : 'Termina'}</Button
							>
							{#if available.length > 0}<span class="text-sm text-muted-foreground"
									>Assegna tutti i piloti: in classifica o tra chi non partecipa.</span
								>{:else if order.length === 0}<span class="text-sm text-muted-foreground"
									>Serve almeno un pilota in classifica.</span
								>{/if}
							{#if busy}<span class="text-sm text-muted-foreground" role="status">Salvataggio…</span
								>{:else if saved && !dirty}<span class="text-sm text-muted-foreground" role="status"
									>Salvato.</span
								>{:else if dirty}<span class="text-sm text-muted-foreground" role="status"
									>Modifiche locali non salvate.</span
								>{/if}
						</div>
						{#if saveError}<p class="text-sm text-destructive" role="alert">{saveError}</p>{/if}
					</form>
				</Card.Content>
			</Card.Root>
		{/if}
	{/if}
</main>
{#if leaveTarget}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
		role="dialog"
		aria-modal="true"
		aria-label="Uscire senza salvare?"
	>
		<div class="w-full max-w-sm space-y-4 rounded-lg border bg-background p-6 shadow-lg">
			<h2 class="text-lg font-semibold">Uscire senza salvare?</h2>
			<p class="text-sm text-muted-foreground">
				Le modifiche locali non salvate andranno perse. Un'eventuale richiesta già inviata non viene
				annullata uscendo.
			</p>
			<div class="flex justify-end gap-2">
				<Button variant="destructive" onclick={confirmLeave}>Esci</Button><Button
					variant="outline"
					onclick={() => (leaveTarget = null)}>Rimani</Button
				>
			</div>
		</div>
	</div>
{/if}
