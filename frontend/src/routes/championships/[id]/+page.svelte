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
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import ChampionshipSettings from '$lib/components/championship-settings.svelte';
	import EnrollPilotDialog from '$lib/components/enroll-pilot-dialog.svelte';
	import PilotGiftButton from '$lib/components/pilot-gift-button.svelte';
	import PilotPickerDialog from '$lib/components/pilot-picker-dialog.svelte';
	import PilotCardPlays from '$lib/components/pilot-card-plays.svelte';
	import CardGiftPopup from '$lib/components/card-gift-popup.svelte';

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
				onUnauthorized: () => { auth.user = null; }
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

<main class="mx-auto max-w-5xl space-y-6 p-6">
	<a href={resolve('/championships')} class="text-sm text-muted-foreground hover:text-foreground">
		← Campionati
	</a>

	{#if liveError}
		<p class="text-sm text-destructive" role="alert">Aggiornamento non riuscito: {liveError}</p>
	{/if}

	{#if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{:else if !championship}
		<p class="text-muted-foreground">Caricamento…</p>
	{:else}
		<div class="flex items-start justify-between gap-3">
			<div>
				<h1 class="text-2xl font-bold">{championship.name}</h1>
				<p class="text-sm text-muted-foreground">
					{new Date(championship.date).toLocaleDateString('it-IT')} ·
					{championship.is_closed ? 'Chiuso' : 'Attivo'}
				</p>
			</div>
			<div class="flex items-center gap-2">
				{#if showEnroll}
					<Button size="sm" variant="outline" onclick={() => (enrollOpen = true)}>
						Iscrivi un pilota
					</Button>
				{/if}
				{#if deckMode !== 'hidden'}
					<Button size="sm" variant="outline" onclick={openDeck}>Vedi mazzo</Button>
				{/if}
				<!-- Campionato chiuso: il negozio si apre in sola lettura, solo per l'admin -->
				{#if !championship.is_closed || auth.isAdmin}
					<a
						href={resolve('/championships/[id]/shop', { id: String(championship.id) })}
						class="inline-flex h-8 items-center rounded-md border border-input bg-background px-3 text-sm hover:bg-accent"
					>
						Negozio
					</a>
				{/if}
				{#if auth.isAdmin}
					<Button
						size="sm"
						variant="outline"
						aria-label="Impostazioni del campionato"
						onclick={() => (settingsOpen = true)}
					>
						⚙
					</Button>
				{/if}
			</div>
		</div>

		<Card.Root>
			<Card.Header>
				<Card.Title>Classifica</Card.Title>
				<Card.Description>{championship.pilots_count} piloti iscritti</Card.Description>
			</Card.Header>
			<Card.Content>
				{#if standings.length === 0}
					<p class="text-sm text-muted-foreground">Nessun pilota iscritto.</p>
				{:else}
					<ol class="divide-y">
						{#each standings as row, index (standingKey(row, index))}
							<li class="flex flex-wrap items-center gap-3 py-2">
								<span class="w-6 text-right text-sm text-muted-foreground">{row.rank}</span>
								<span class="flex-1 font-medium">
									{row.pilot_name}
									{#if row.pilot_id !== null && myIds.has(row.pilot_id)}
										<span class="ml-2 text-xs text-muted-foreground">(tuo)</span>
									{/if}
								</span>
								<span class="text-xs text-muted-foreground">
									{row.races_played}
									{row.races_played === 1 ? 'gara' : 'gare'}
								</span>
								<span class="w-20 text-right text-sm">{row.points} punti</span>
								{#if canGift && row.pilot_id !== null}
									<PilotGiftButton
										championshipId={championship.id}
										pilot={{ id: row.pilot_id, name: row.pilot_name }}
										showName={false}
									/>
								{/if}
							</li>
						{/each}
					</ol>
				{/if}
			</Card.Content>
		</Card.Root>

		{#if raceInProgress && !championship.is_closed && enrolled.length > 0}
			<Card.Root>
				<Card.Header>
					<Card.Title>Le tue carte sponsor</Card.Title>
					<Card.Description>Gioca le carte dei tuoi piloti nella gara in corso.</Card.Description>
				</Card.Header>
				<Card.Content class="space-y-3">
					{#each enrolled as p (p.id)}
						<PilotCardPlays
							championshipId={championship.id}
							pilot={p}
							startOpen={enrolled.length === 1}
							refreshKey={giftTick}
						/>
					{/each}
				</Card.Content>
			</Card.Root>
		{/if}

		<Card.Root>
			<Card.Header>
				<Card.Title>Gare</Card.Title>
				<Card.Description>{races.length} gare in calendario</Card.Description>
			</Card.Header>
			<Card.Content>
				{#if auth.canManageRaces && !championship.is_closed}
					<div class="mb-4">
						<Button
							size="sm"
							onclick={createRace}
							disabled={busy}
							aria-disabled={raceUnfinished}
							class={raceUnfinished ? 'opacity-50' : ''}
						>
							Nuova gara
						</Button>
						{#if raceError}
							<p class="mt-3 text-sm text-destructive" role="alert">{raceError}</p>
						{/if}
					</div>
				{/if}
				{#if races.length === 0}
					<p class="text-sm text-muted-foreground">Nessuna gara ancora disputata.</p>
				{:else}
					<ul class="divide-y">
						{#each sortedRaces as race (race.id)}
							<li>
								<a
									href={resolve('/championships/[id]/races/[raceId]', {
										id: String(championship.id),
										raceId: String(race.id)
									})}
									class="flex items-center gap-3 py-2 hover:bg-accent"
								>
									<span class="flex-1 font-medium">Gara {race.number}</span>
									<span class="text-sm text-muted-foreground">{raceDate(race.date)}</span>
									<span class={`text-sm font-medium ${raceStatusView(race.status).class}`}>
										{raceStatusView(race.status).label}
									</span>
								</a>
							</li>
						{/each}
					</ul>
				{/if}
			</Card.Content>
		</Card.Root>

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
