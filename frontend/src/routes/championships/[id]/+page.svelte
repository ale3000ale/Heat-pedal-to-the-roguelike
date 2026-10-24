<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { api } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import { standingKey } from '$lib/standings';
	import { canShowEnroll, enrollablePilots } from '$lib/enroll-candidates';
	import { deckAction } from '$lib/deck-access';
	import { raceStatusView } from '$lib/race-status';
	import { loadPollIntervalMs } from '$lib/card-poll.svelte';
	import { startChampionshipLive } from '$lib/championship-live';
	import type { CardGift } from '$lib/card-play-types';
	import type { ChampionshipDetail, Pilot } from '$lib/types';
	import type { Race, Standing } from '$lib/race-types';
	import { Button } from '$lib/components/ui/button';
	import ChampionshipSettings from '$lib/components/championship-settings.svelte';
	import EnrollPilotDialog from '$lib/components/enroll-pilot-dialog.svelte';
	import PilotGiftButton from '$lib/components/pilot-gift-button.svelte';
	import PilotPickerDialog from '$lib/components/pilot-picker-dialog.svelte';
	import PilotCardPlays from '$lib/components/pilot-card-plays.svelte';
	import CardGiftPopup from '$lib/components/card-gift-popup.svelte';
	import RacingIcon from '$lib/components/racing-icon.svelte';

	const RACE_UNFINISHED_MESSAGE =
		"C'è una gara non conclusa (in corso o in revisione): va conclusa prima di crearne un'altra.";

	let championship = $state<ChampionshipDetail | null>(null);
	let standings = $state<Standing[]>([]);
	let races = $state<Race[]>([]);
	let myPilots = $state<Pilot[]>([]);
	let error = $state<string | null>(null);
	let liveError = $state<string | null>(null);
	let raceError = $state<string | null>(null);
	let busy = $state(false);
	let settingsOpen = $state(false);
	let enrollOpen = $state(false);
	let deckOpen = $state(false);
	let gifts = $state<CardGift[]>([]);
	let giftOpen = $state(false);
	// Ogni snapshot applicato aggiorna anche le sezioni sponsor aperte.
	let giftTick = $state(0);
	let currentLive: ReturnType<typeof startChampionshipLive> | null = null;

	let myIds = $derived(new Set(myPilots.map((p) => p.id)));
	let candidates = $derived(enrollablePilots(myPilots));
	let enrolled = $derived(
		myPilots.filter((p) => championship?.pilots.some((entrant) => entrant.id === p.id))
	);
	let showEnroll = $derived(
		championship !== null && canShowEnroll(championship.is_closed, enrolled.length)
	);
	let deckMode = $derived(
		championship ? deckAction(championship.is_closed, enrolled.length) : 'hidden'
	);
	let raceInProgress = $derived(races.some((race) => race.participants === 0));
	let raceUnfinished = $derived(races.some((race) => race.status !== 'closed'));
	let canGift = $derived(
		championship !== null && !championship.is_closed && auth.canManageRaces && raceInProgress
	);
	let sortedRaces = $derived(
		[...races].sort((a, b) => {
			const byDate = raceTime(b.date) - raceTime(a.date);
			return byDate !== 0 ? byDate : b.number - a.number;
		})
	);

	function raceTime(value: string | null): number {
		const time = value ? new Date(value).getTime() : 0;
		return Number.isNaN(time) ? 0 : time;
	}

	function raceDate(value: string | null): string {
		return value ? new Date(value).toLocaleDateString('it-IT') : 'Data da definire';
	}

	/**
	 * Rilegge attraverso la stessa coda live dopo azioni REST della pagina o dei dialoghi.
	 * @returns Attende lo svuotamento della coda; gli errori sono mostrati dai callback live.
	 */
	async function reload(): Promise<void> {
		await currentLive?.refresh();
	}

	async function afterDelete() {
		currentLive?.dispose();
		await goto(resolve('/championships'));
	}

	/**
	 * Conferma soltanto le notifiche rese dal popup chiuso volontariamente.
	 * @param shown Ultima lista resa dal componente; non la coda delle notifiche nuove.
	 * @returns Attende conferma e rilettura. Errori e 401 sono gestiti dal modulo live.
	 */
	async function onGiftsClosed(shown: CardGift[]): Promise<void> {
		if (!auth.user) return;
		await currentLive?.close(shown.map((gift) => gift.id));
	}

	// Il contesto dipende solo da parametro e utente, non dagli snapshot applicati.
	// Dispose invalida risposte tardive; una lettura dell'intervallo tardiva non avvia lavoro.
	$effect(() => {
		const championshipId = Number(page.params.id);
		const userId = auth.user?.id;
		championship = null;
		standings = [];
		races = [];
		myPilots = [];
		gifts = [];
		giftOpen = false;
		giftTick = 0;
		error = null;
		liveError = null;
		raceError = null;
		busy = false;
		settingsOpen = false;
		enrollOpen = false;
		deckOpen = false;
		if (!userId) return;
		if (!Number.isSafeInteger(championshipId) || championshipId < 1) {
			error = 'Campionato non valido';
			return;
		}
		let cancelled = false;
		let active: ReturnType<typeof startChampionshipLive> | null = null;
		void loadPollIntervalMs().then((intervalMs) => {
			if (cancelled) return;
			active = startChampionshipLive({
				championshipId,
				intervalMs,
				onSnapshot: (snapshot) => {
					championship = snapshot.championship;
					standings = snapshot.standings;
					races = snapshot.races;
					myPilots = snapshot.myPilots;
					error = null;
					liveError = null;
					giftTick += 1;
				},
				onGifts: (visible) => {
					gifts = visible.map(({ gift }) => gift);
					giftOpen = visible.length > 0;
				},
				onError: (cause) => {
					const message = cause instanceof Error ? cause.message : 'Errore sconosciuto';
					if (championship) liveError = message;
					else error = message;
				},
				onUnauthorized: () => {
					auth.user = null;
				}
			});
			currentLive = active;
		});
		return () => {
			cancelled = true;
			active?.dispose();
			if (currentLive === active) currentLive = null;
		};
	});

	// La finestra chiede gia' conferma. Il refresh comprende anche l'elenco dei piloti.
	async function enrollPilot(pilotId: number) {
		const active = currentLive;
		const championshipId = Number(page.params.id);
		await api(`/championships/${championshipId}/pilots`, {
			method: 'POST',
			body: { pilot_id: pilotId }
		});
		if (active === currentLive) await active?.refresh();
	}

	function goToDeck(pilot: Pilot) {
		void goto(resolve('/pilots/[id]', { id: String(pilot.id) }));
	}

	function openDeck() {
		if (deckMode === 'choose') deckOpen = true;
		else if (enrolled.length > 0) goToDeck(enrolled[0]);
	}

	// La lettura dopo POST usa la coda live, senza applicare risposte del vecchio contesto.
	async function createRace() {
		if (raceUnfinished) {
			raceError = RACE_UNFINISHED_MESSAGE;
			return;
		}
		const active = currentLive;
		const championshipId = Number(page.params.id);
		raceError = null;
		busy = true;
		try {
			await api<Race>(`/championships/${championshipId}/races`, { method: 'POST' });
			if (active === currentLive) await active?.refresh();
		} catch (e) {
			if (active === currentLive) {
				raceError = e instanceof Error ? e.message : 'Errore sconosciuto';
			}
		} finally {
			if (active === currentLive) busy = false;
		}
	}
</script>

<svelte:head><title>{championship ? championship.name : 'Campionato'} - Heat</title></svelte:head>

<main class="mx-auto max-w-6xl space-y-6 px-4 py-8 sm:px-6">
	<div
		class="flex items-center gap-2 font-racing text-xs tracking-wider text-muted-foreground uppercase"
	>
		<a
			href={resolve('/championships')}
			class="inline-flex items-center gap-1 transition-colors hover:text-white"
		>
			<span>←</span>
			<span>Tutti i Campionati</span>
		</a>
		<span>/</span>
		<span class="font-bold text-white">{championship ? championship.name : 'Dettagli'}</span>
	</div>

	{#if liveError}
		<div
			class="flex items-center gap-2 rounded-xl border border-destructive/40 bg-destructive/15 p-3 text-xs text-red-300"
			role="alert"
		>
			<RacingIcon name="flame" size="xs" />
			<span>Aggiornamento non riuscito: {liveError}</span>
		</div>
	{/if}

	{#if error}
		<div
			class="flex items-center gap-2 rounded-xl border border-destructive/40 bg-destructive/15 p-3 text-xs text-red-300"
			role="alert"
		>
			<RacingIcon name="flame" size="xs" />
			<span>{error}</span>
		</div>
	{:else if !championship}
		<div class="flex items-center justify-center p-12 text-muted-foreground">
			<RacingIcon name="speedometer" size="lg" class="mr-3 animate-spin text-primary" />
			<span class="font-racing text-lg tracking-wider uppercase"
				>Accesso alla telemetria del campionato…</span
			>
		</div>
	{:else}
		<!-- Championship Header Banner with board game background -->
		<div class="relative overflow-hidden rounded-2xl border border-white/10 bg-[#121622] shadow-xl">
			<!-- Board game photo background (right side) -->
			<div class="absolute inset-0 z-0">
				<img
					src="/images/heat-corner.jpg"
					alt="Heat miniature in curva"
					class="h-full w-full object-cover object-center opacity-15"
				/>
				<div
					class="absolute inset-0 bg-gradient-to-r from-[#121622] via-[#121622]/90 to-[#121622]/50"
				></div>
			</div>
			<div class="curb-bar relative z-10" role="presentation"></div>
			<div
				class="relative z-10 flex flex-col justify-between gap-6 p-6 md:flex-row md:items-center"
			>
				<div>
					<div class="mb-2 flex items-center gap-2.5">
						{#if championship.is_closed}
							<span
								class="inline-flex items-center gap-1 rounded-full border border-white/10 bg-white/10 px-2.5 py-0.5 text-xs font-bold tracking-wider text-muted-foreground uppercase"
							>
								<RacingIcon name="flags" size="xs" />
								Campionato Chiuso
							</span>
						{:else}
							<span
								class="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/15 px-2.5 py-0.5 text-xs font-bold tracking-wider text-emerald-400 uppercase"
							>
								<span class="h-2 w-2 animate-pulse rounded-full bg-emerald-400"></span>
								Campionato Attivo
							</span>
						{/if}
						<span class="text-xs text-muted-foreground">
							{new Date(championship.date).toLocaleDateString('it-IT', {
								day: '2-digit',
								month: 'long',
								year: 'numeric'
							})}
						</span>
					</div>

					<h1
						class="font-racing text-3xl font-black tracking-wide text-white uppercase italic sm:text-4xl"
					>
						{championship.name}
					</h1>
					<p class="mt-1 text-xs tracking-widest text-muted-foreground uppercase">
						{championship.pilots_count}
						{championship.pilots_count === 1 ? 'pilota iscritto' : 'piloti iscritti'} · {races.length}
						gare
					</p>
				</div>

				<div class="flex flex-wrap items-center gap-2.5">
					{#if showEnroll}
						<Button
							size="sm"
							class="heat-glow h-9 bg-primary font-racing font-bold tracking-wider text-white uppercase hover:bg-accent"
							onclick={() => (enrollOpen = true)}
						>
							<RacingIcon name="helmet" size="xs" class="mr-1.5" />
							Iscrivi un pilota
						</Button>
					{/if}
					{#if deckMode !== 'hidden'}
						<Button
							size="sm"
							variant="outline"
							class="h-9 border-white/15 bg-white/5 font-racing font-bold tracking-wider text-white uppercase hover:bg-white/10"
							onclick={openDeck}
						>
							<RacingIcon name="speedometer" size="xs" class="mr-1.5" />
							Vedi mazzo
						</Button>
					{/if}
					{#if !championship.is_closed || auth.isAdmin}
						<a
							href={resolve('/championships/[id]/shop', { id: String(championship.id) })}
							class="inline-flex h-9 items-center gap-1.5 rounded-lg border border-sky-500/30 bg-sky-500/10 px-3 font-racing text-xs font-bold tracking-wider text-sky-400 uppercase transition-colors hover:bg-sky-500/20"
						>
							<RacingIcon name="tires" size="xs" />
							<span>Negozio</span>
						</a>
					{/if}
					{#if auth.isAdmin}
						<Button
							size="sm"
							variant="outline"
							class="h-9 w-9 rounded-lg border-white/15 bg-white/5 p-0 text-muted-foreground hover:border-amber-400 hover:text-amber-400"
							aria-label="Impostazioni del campionato"
							onclick={() => (settingsOpen = true)}
						>
							<RacingIcon name="wrenches" size="xs" />
						</Button>
					{/if}
				</div>
			</div>
		</div>

		<!-- Grand Prix Leaderboard / Classifica Ufficiale -->
		<div class="overflow-hidden rounded-2xl border border-white/10 bg-[#121622] shadow-xl">
			<div
				class="flex items-center justify-between border-b border-white/10 bg-[#171c28] px-5 py-4"
			>
				<div class="flex items-center gap-2.5">
					<div
						class="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-500/20 text-amber-400"
					>
						<RacingIcon name="trophy" size="sm" />
					</div>
					<div>
						<h2 class="font-racing text-2xl font-bold tracking-wide text-white uppercase">
							Classifica Generale Piloti
						</h2>
						<p class="mt-0.5 text-xs text-muted-foreground">
							Punteggio cumulativo delle gare disputate
						</p>
					</div>
				</div>
				<span class="font-racing text-xs tracking-wider text-muted-foreground uppercase">
					{standings.length} Piloti
				</span>
			</div>

			<div class="p-4 sm:p-5">
				{#if standings.length === 0}
					<p class="py-8 text-center text-xs text-muted-foreground italic">
						Nessun pilota ancora iscritto alla griglia di partenza.
					</p>
				{:else}
					<ol class="space-y-2">
						{#each standings as row, index (standingKey(row, index))}
							{@const isFirst = row.rank === 1}
							{@const isSecond = row.rank === 2}
							{@const isThird = row.rank === 3}
							{@const isMine = row.pilot_id !== null && myIds.has(row.pilot_id)}
							<li
								class="flex flex-wrap items-center justify-between gap-3 rounded-xl border p-3.5 transition-all {isFirst
									? 'border-amber-500/40 bg-amber-500/10 shadow-sm'
									: isMine
										? 'border-primary/30 bg-primary/10'
										: 'border-white/5 bg-[#161a26] hover:border-white/15'}"
							>
								<div class="flex items-center gap-3.5">
									<!-- Position badge -->
									{#if isFirst}
										<div
											class="gold-glow flex h-8 w-8 items-center justify-center rounded-full bg-amber-500 font-racing text-sm font-black text-black shadow-md"
										>
											<RacingIcon name="trophy" size="xs" />
										</div>
									{:else if isSecond}
										<div
											class="flex h-8 w-8 items-center justify-center rounded-full bg-slate-300 font-racing text-sm font-black text-black shadow-md"
										>
											<RacingIcon name="laurel" size="xs" />
										</div>
									{:else if isThird}
										<div
											class="flex h-8 w-8 items-center justify-center rounded-full bg-amber-800 font-racing text-sm font-black text-amber-100 shadow-md"
										>
											3
										</div>
									{:else}
										<div
											class="flex h-8 w-8 items-center justify-center rounded-full border border-white/10 bg-white/5 font-racing text-xs font-bold text-muted-foreground"
										>
											{row.rank}
										</div>
									{/if}

									<!-- Pilot Name -->
									<div class="flex items-center gap-2">
										<span
											class="text-base font-bold tracking-wide text-white {isFirst
												? 'font-black text-amber-300'
												: ''}"
										>
											{row.pilot_name}
										</span>
										{#if isMine}
											<span
												class="rounded border border-primary/30 bg-primary/25 px-1.5 py-0.5 font-racing text-[10px] font-bold tracking-wider text-primary uppercase"
											>
												Tuo Pilota
											</span>
										{/if}
									</div>
								</div>

								<!-- Stats & Points -->
								<div class="flex items-center gap-4">
									<span class="text-xs text-muted-foreground">
										{row.races_played}
										{row.races_played === 1 ? 'gara' : 'gare'}
									</span>

									<div class="min-w-[80px] text-right">
										<span
											class="font-racing text-2xl font-black tracking-wide italic {isFirst
												? 'text-amber-400'
												: 'text-white'}"
										>
											{row.points}
										</span>
										<span class="ml-0.5 text-[10px] font-bold text-muted-foreground uppercase"
											>PTS</span
										>
									</div>

									{#if canGift && row.pilot_id !== null}
										<PilotGiftButton
											championshipId={championship.id}
											pilot={{ id: row.pilot_id, name: row.pilot_name }}
											showName={false}
										/>
									{/if}
								</div>
							</li>
						{/each}
					</ol>
				{/if}
			</div>
		</div>

		{#if raceInProgress && !championship.is_closed && enrolled.length > 0}
			<div
				class="curb-top overflow-hidden rounded-2xl border border-primary/30 bg-[#121622] shadow-xl"
			>
				<div
					class="flex items-center justify-between border-b border-white/10 bg-[#191522] px-5 py-4"
				>
					<div class="flex items-center gap-2.5">
						<div
							class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/20 text-primary"
						>
							<RacingIcon name="flame" size="sm" />
						</div>
						<div>
							<h2 class="font-racing text-2xl font-bold tracking-wide text-white uppercase">
								Le Tue Carte Sponsor in Gara
							</h2>
							<p class="mt-0.5 text-xs text-muted-foreground">
								Gioca le carte dei tuoi piloti nella gara attualmente in corso
							</p>
						</div>
					</div>
				</div>
				<div class="space-y-3 p-5">
					{#each enrolled as p (p.id)}
						<PilotCardPlays
							championshipId={championship.id}
							pilot={p}
							startOpen={enrolled.length === 1}
							refreshKey={giftTick}
						/>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Races Section -->
		<div class="overflow-hidden rounded-2xl border border-white/10 bg-[#121622] shadow-xl">
			<div
				class="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 bg-[#171c28] px-5 py-4"
			>
				<div class="flex items-center gap-2.5">
					<div
						class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/20 text-primary"
					>
						<RacingIcon name="flags" size="sm" />
					</div>
					<div>
						<h2 class="font-racing text-2xl font-bold tracking-wide text-white uppercase">
							Gare in Calendario
						</h2>
						<p class="mt-0.5 text-xs text-muted-foreground">
							{races.length} gare disputate o programmate
						</p>
					</div>
				</div>

				{#if auth.canManageRaces && !championship.is_closed}
					<Button
						size="sm"
						onclick={createRace}
						disabled={busy}
						aria-disabled={raceUnfinished}
						class="heat-glow h-9 bg-primary font-racing font-bold tracking-wider text-white uppercase hover:bg-accent {raceUnfinished
							? 'cursor-not-allowed opacity-50'
							: ''}"
					>
						<RacingIcon name="flags" size="xs" class="mr-1.5" />
						Nuova Gara
					</Button>
				{/if}
			</div>

			<div class="p-4 sm:p-5">
				{#if raceError}
					<div
						class="mb-4 rounded-lg border border-destructive/40 bg-destructive/15 p-2.5 text-xs text-red-300"
						role="alert"
					>
						{raceError}
					</div>
				{/if}

				{#if races.length === 0}
					<p class="py-8 text-center text-xs text-muted-foreground italic">
						Nessuna gara ancora disputata in questo campionato.
					</p>
				{:else}
					<ul class="space-y-2.5">
						{#each sortedRaces as race (race.id)}
							{@const statusInfo = raceStatusView(race.status)}
							<li>
								<a
									href={resolve('/championships/[id]/races/[raceId]', {
										id: String(championship.id),
										raceId: String(race.id)
									})}
									class="group flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/5 bg-[#161a26] p-4 transition-all hover:border-primary/40 hover:bg-[#1b2030]"
								>
									<div class="flex items-center gap-3.5">
										<div class="racing-roundel h-8 w-8 text-xs font-black">
											{race.number}
										</div>
										<div>
											<span
												class="group-hover:text-heat text-base font-bold tracking-wide text-white transition-colors"
											>
												Gran Premio - Gara #{race.number}
											</span>
											<span class="mt-0.5 block text-xs text-muted-foreground">
												{raceDate(race.date)}
											</span>
										</div>
									</div>

									<div class="flex items-center gap-3">
										<span
											class="rounded-full border px-3 py-1 font-racing text-xs font-bold tracking-wider uppercase {statusInfo.class}"
										>
											{statusInfo.label}
										</span>
										<span
											class="text-xs font-bold text-primary transition-transform group-hover:translate-x-1"
											>→</span
										>
									</div>
								</a>
							</li>
						{/each}
					</ul>
				{/if}
			</div>
		</div>

		{#if auth.isAdmin}
			<ChampionshipSettings
				{championship}
				bind:open={settingsOpen}
				onclosed={reload}
				ondeleted={afterDelete}
			/>
		{/if}

		<EnrollPilotDialog
			bind:open={enrollOpen}
			championshipName={championship.name}
			pilots={candidates}
			onenroll={enrollPilot}
		/>

		<PilotPickerDialog
			bind:open={deckOpen}
			title="Mazzo di quale pilota?"
			pilots={enrolled}
			onselect={goToDeck}
		/>

		<CardGiftPopup bind:open={giftOpen} {gifts} onclosed={onGiftsClosed} />
	{/if}
</main>
