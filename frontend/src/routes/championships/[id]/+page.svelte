<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { api } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import { standingKey } from '$lib/standings';
	import { canShowEnroll, enrollablePilots } from '$lib/enroll-candidates';
	import { deckAction } from '$lib/deck-access';
	import { raceStatusView } from '$lib/race-status';
	import {
		fetchUnseenGifts,
		loadPollIntervalMs,
		markGiftsSeen,
		startGiftPolling
	} from '$lib/card-poll.svelte';
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
	let raceError = $state<string | null>(null);
	let busy = $state(false);
	let settingsOpen = $state(false);
	let enrollOpen = $state(false);
	let deckOpen = $state(false);
	let gifts = $state<CardGift[]>([]);
	let giftOpen = $state(false);
	// Aumenta a ogni controllo periodico: fa rileggere in silenzio le carte giocabili.
	let giftTick = $state(0);

	let myIds = $derived(new Set(myPilots.map((p) => p.id)));
	// Piloti che si possono iscrivere: hanno un team e non sono in nessun campionato attivo.
	let candidates = $derived(enrollablePilots(myPilots));
	// I miei piloti iscritti a questo campionato: sono quelli che giocano le carte sponsor.
	let enrolled = $derived(
		myPilots.filter((p) => championship?.pilots.some((entrant) => entrant.id === p.id))
	);
	// Il pulsante d'iscrizione c'è solo in un campionato attivo senza miei piloti iscritti.
	let showEnroll = $derived(
		championship !== null && canShowEnroll(championship.is_closed, enrolled.length)
	);
	// Cosa fa il pulsante del mazzo: nascosto, apre il pilota oppure chiede quale pilota.
	let deckMode = $derived(
		championship ? deckAction(championship.is_closed, enrolled.length) : 'hidden'
	);
	// Una gara senza classifica è in corso: carte sponsor e tasto S valgono solo finché c'è.
	let raceInProgress = $derived(races.some((race) => race.participants === 0));
	// Una gara non è conclusa finché è in corso o in revisione: finché c'è non se ne può
	// creare un'altra (lo stesso controllo del backend).
	let raceUnfinished = $derived(races.some((race) => race.status !== 'closed'));
	// Il tasto S accanto ai piloti compare solo a giudice e admin, con una gara in corso.
	let canGift = $derived(
		championship !== null && !championship.is_closed && auth.canManageRaces && raceInProgress
	);
	// Gare dalla più recente: per data decrescente, a parità (o senza data) per numero.
	let sortedRaces = $derived(
		[...races].sort((a, b) => {
			const byDate = raceTime(b.date) - raceTime(a.date);
			return byDate !== 0 ? byDate : b.number - a.number;
		})
	);

	// Istante della data in millisecondi; una data non impostata vale 0 (in fondo all'elenco).
	function raceTime(value: string | null): number {
		const time = value ? new Date(value).getTime() : 0;
		return Number.isNaN(time) ? 0 : time;
	}

	// La data della gara può non essere impostata (gare create prima della data automatica).
	function raceDate(value: string | null): string {
		return value ? new Date(value).toLocaleDateString('it-IT') : 'Data da definire';
	}

	// Ricarica i dati del campionato che cambiano dopo un'iscrizione o una chiusura.
	async function reload() {
		[championship, standings] = await Promise.all([
			api<ChampionshipDetail>(`/championships/${page.params.id}`),
			api<Standing[]>(`/championships/${page.params.id}/standings`)
		]);
	}

	async function afterDelete() {
		await goto(resolve('/championships'));
	}

	// Controllo periodico. Prima fa rileggere le carte giocabili (una carta ricevuta o annullata
	// compare entro l'intervallo, senza ricaricare la pagina), poi, se c'è una carta ottenuta
	// non vista, apre il popup. Mentre il popup è aperto non cerca altre notifiche, così non
	// si accavallano.
	async function checkGifts(championshipId: number, pilotIds: number[]) {
		giftTick += 1;
		if (giftOpen) return;
		const found = await fetchUnseenGifts(championshipId, pilotIds);
		if (found.length > 0 && !giftOpen) {
			gifts = found;
			giftOpen = true;
		}
	}

	// Alla chiusura del popup le notifiche dei miei piloti risultano viste.
	async function onGiftsClosed() {
		if (!championship) return;
		try {
			await markGiftsSeen(
				championship.id,
				enrolled.map((p) => p.id)
			);
		} catch {
			// Se non si riesce a segnarle, riappariranno al prossimo controllo.
		}
		gifts = [];
	}

	// Avvia il controllo periodico quando ci sono piloti miei iscritti a un campionato attivo.
	// L'intervallo è quello impostato dall'admin: va letto prima di avviare il controllo, e se
	// la pagina cambia nel frattempo `cancelled` impedisce di avviarlo dopo la chiusura.
	$effect(() => {
		if (!championship || championship.is_closed) return;
		const championshipId = championship.id;
		const pilotIds = enrolled.map((p) => p.id);
		if (pilotIds.length === 0) return;
		let stop: (() => void) | null = null;
		let cancelled = false;
		void loadPollIntervalMs().then((intervalMs) => {
			if (cancelled) return;
			stop = startGiftPolling(() => checkGifts(championshipId, pilotIds), intervalMs);
		});
		return () => {
			cancelled = true;
			stop?.();
		};
	});

	onMount(async () => {
		try {
			[championship, standings, races, myPilots] = await Promise.all([
				api<ChampionshipDetail>(`/championships/${page.params.id}`),
				api<Standing[]>(`/championships/${page.params.id}/standings`),
				api<Race[]>(`/championships/${page.params.id}/races`),
				api<Pilot[]>('/pilots')
			]);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		}
	});

	// Iscrive un proprio pilota (la finestra ha già chiesto la conferma) e ricarica campionato
	// e piloti: l'iscrizione cambia sia la classifica sia il campionato attivo del pilota.
	// Se la richiesta fallisce lancia l'errore, che la finestra mostra all'utente.
	async function enrollPilot(pilotId: number) {
		await api(`/championships/${page.params.id}/pilots`, {
			method: 'POST',
			body: { pilot_id: pilotId }
		});
		await reload();
		myPilots = await api<Pilot[]>('/pilots');
	}

	// Apre la pagina del pilota, dove si vedono e si modificano mazzo e inventario.
	function goToDeck(pilot: Pilot) {
		void goto(resolve('/pilots/[id]', { id: String(pilot.id) }));
	}

	// Con un solo pilota iscritto va dritta alla sua pagina, altrimenti chiede quale.
	function openDeck() {
		if (deckMode === 'choose') deckOpen = true;
		else if (enrolled.length > 0) goToDeck(enrolled[0]);
	}

	// Admin e giudice: crea la prossima gara. Resta in questa pagina: la gara nuova
	// compare in lista come "in corso" e si apre da lì. Con una gara non conclusa il pulsante
	// sembra spento ma si può premere: il click mostra solo l'avviso, senza chiamare l'API.
	async function createRace() {
		if (raceUnfinished) {
			raceError = RACE_UNFINISHED_MESSAGE;
			return;
		}
		raceError = null;
		busy = true;
		try {
			const created = await api<Race>(`/championships/${page.params.id}/races`, {
				method: 'POST'
			});
			races = [...races, created];
		} catch (e) {
			raceError = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			busy = false;
		}
	}
</script>

<svelte:head><title>{championship ? championship.name : 'Campionato'} - Heat</title></svelte:head>

<main class="mx-auto max-w-5xl space-y-6 p-6">
	<a href={resolve('/championships')} class="text-sm text-muted-foreground hover:text-foreground">
		← Campionati
	</a>

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
