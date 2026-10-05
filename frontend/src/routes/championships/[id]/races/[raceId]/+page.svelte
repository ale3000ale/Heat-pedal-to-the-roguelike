<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { api } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import type { ChampionshipDetail, Pilot } from '$lib/types';
	import type { RaceDetail } from '$lib/race-types';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';

	// Una riga del modulo: un pilota in ordine di arrivo con i suoi punti sponsor.
	interface Row {
		pilot_id: number;
		name: string;
		sponsor: number;
	}

	const MAX_PARTICIPANTS = 12;
	const inputClass =
		'h-8 w-20 rounded-md border border-input bg-background px-2 text-sm disabled:opacity-50';

	let race = $state<RaceDetail | null>(null);
	let championship = $state<ChampionshipDetail | null>(null);
	let myPilots = $state<Pilot[]>([]);
	let order = $state<Row[]>([]);
	let error = $state<string | null>(null);
	let saveError = $state<string | null>(null);
	let saved = $state(false);
	let busy = $state(false);

	let myIds = $derived(new Set(myPilots.map((p) => p.id)));
	// Una gara con almeno un risultato è chiusa.
	let isRaceClosed = $derived(race !== null && race.participants > 0);
	// Il giudice può chiudere una gara aperta; solo l'admin può correggerne una chiusa.
	// Un campionato chiuso è in sola lettura per tutti.
	let canEdit = $derived(
		championship !== null &&
			!championship.is_closed &&
			auth.canManageRaces &&
			(!isRaceClosed || auth.canCorrectRaces)
	);
	// Iscritti non ancora messi nell'ordine di arrivo.
	let available = $derived(
		race ? race.results.filter((r) => !order.some((row) => row.pilot_id === r.pilot_id)) : []
	);

	// La data della gara può non essere impostata.
	function raceDate(value: string | null): string {
		return value ? new Date(value).toLocaleDateString('it-IT') : 'Data da definire';
	}

	// Riempie il modulo con i partecipanti già registrati, nell'ordine di arrivo.
	function loadOrder(detail: RaceDetail) {
		order = detail.results
			.filter((r) => r.position !== null)
			.map((r) => ({ pilot_id: r.pilot_id, name: r.pilot_name, sponsor: r.sponsor_points }));
	}

	function addToOrder(pilotId: number) {
		const found = race?.results.find((r) => r.pilot_id === pilotId);
		if (!found || order.length >= MAX_PARTICIPANTS) return;
		order.push({ pilot_id: found.pilot_id, name: found.pilot_name, sponsor: 0 });
	}

	function removeFromOrder(index: number) {
		order.splice(index, 1);
	}

	// Sposta un pilota di una posizione: delta -1 sale, +1 scende.
	function move(index: number, delta: -1 | 1) {
		const target = index + delta;
		if (target < 0 || target >= order.length) return;
		const [row] = order.splice(index, 1);
		order.splice(target, 0, row);
	}

	// Il campo numerico può restare vuoto: lo trattiamo come 0 e non accettiamo negativi.
	function cleanSponsor(value: unknown): number {
		const n = Math.trunc(Number(value));
		return Number.isFinite(n) && n > 0 ? n : 0;
	}

	async function save(event: SubmitEvent) {
		event.preventDefault();
		if (order.length === 0) return;
		saveError = null;
		saved = false;
		busy = true;
		try {
			const updated = await api<RaceDetail>(
				`/championships/${page.params.id}/races/${page.params.raceId}/results`,
				{
					method: 'PUT',
					body: {
						results: order.map((row) => ({
							pilot_id: row.pilot_id,
							sponsor_points: cleanSponsor(row.sponsor)
						}))
					}
				}
			);
			race = updated;
			loadOrder(updated);
			saved = true;
		} catch (e) {
			saveError = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			busy = false;
		}
	}

	onMount(async () => {
		try {
			[race, championship, myPilots] = await Promise.all([
				api<RaceDetail>(`/championships/${page.params.id}/races/${page.params.raceId}`),
				api<ChampionshipDetail>(`/championships/${page.params.id}`),
				api<Pilot[]>('/pilots')
			]);
			loadOrder(race);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		}
	});
</script>

<svelte:head><title>{race ? `Gara ${race.number}` : 'Gara'} - Heat</title></svelte:head>

<main class="mx-auto max-w-5xl space-y-6 p-6">
	<a
		href={resolve('/championships/[id]', { id: page.params.id ?? '' })}
		class="text-sm text-muted-foreground hover:text-foreground"
	>
		← Campionato
	</a>

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
				{isRaceClosed ? 'Chiusa' : 'Da disputare'}
			</p>
		</div>

		<Card.Root>
			<Card.Header>
				<Card.Title>Risultati</Card.Title>
				<Card.Description>Chi non ha partecipato ha 0 punti.</Card.Description>
			</Card.Header>
			<Card.Content>
				{#if race.results.length === 0}
					<p class="text-sm text-muted-foreground">Nessun risultato registrato.</p>
				{:else}
					<ol class="divide-y">
						{#each race.results as result (result.pilot_id)}
							<li class="flex items-center gap-3 py-2">
								<span class="w-6 text-right text-sm text-muted-foreground">
									{result.position ?? '–'}
								</span>
								<span class="flex-1 font-medium">
									{result.pilot_name}
									{#if myIds.has(result.pilot_id)}
										<span class="ml-2 text-xs text-muted-foreground">(tuo)</span>
									{/if}
								</span>
								<span class="text-xs text-muted-foreground">
									{result.sponsor_points} sponsor
								</span>
								<span class="w-20 text-right text-sm">{result.points} punti</span>
							</li>
						{/each}
					</ol>
				{/if}
			</Card.Content>
		</Card.Root>

		{#if canEdit}
			<Card.Root>
				<Card.Header>
					<Card.Title>{isRaceClosed ? 'Correggi i risultati' : 'Chiudi la gara'}</Card.Title>
					<Card.Description>
						Metti i piloti in ordine di arrivo (massimo {MAX_PARTICIPANTS}) e indica i punti sponsor
						di ciascuno. Gli sponsor vengono assegnati al salvataggio.
					</Card.Description>
				</Card.Header>
				<Card.Content class="space-y-4">
					<form onsubmit={save} class="space-y-4">
						{#if order.length === 0}
							<p class="text-sm text-muted-foreground">Aggiungi i piloti che hanno partecipato.</p>
						{:else}
							<ol class="divide-y">
								{#each order as row, index (row.pilot_id)}
									<li class="flex flex-wrap items-center gap-2 py-2">
										<span class="w-6 text-right text-sm text-muted-foreground">{index + 1}</span>
										<span class="min-w-32 flex-1 font-medium">{row.name}</span>
										<label class="flex items-center gap-1 text-sm text-muted-foreground">
											Sponsor
											<input
												type="number"
												min="0"
												step="1"
												class={inputClass}
												bind:value={row.sponsor}
												aria-label={`Punti sponsor di ${row.name}`}
											/>
										</label>
										<Button
											type="button"
											size="sm"
											variant="outline"
											disabled={index === 0}
											onclick={() => move(index, -1)}
											aria-label={`Sposta su ${row.name}`}
										>
											↑
										</Button>
										<Button
											type="button"
											size="sm"
											variant="outline"
											disabled={index === order.length - 1}
											onclick={() => move(index, 1)}
											aria-label={`Sposta giù ${row.name}`}
										>
											↓
										</Button>
										<Button
											type="button"
											size="sm"
											variant="ghost"
											onclick={() => removeFromOrder(index)}
											aria-label={`Togli ${row.name}`}
										>
											Togli
										</Button>
									</li>
								{/each}
							</ol>
						{/if}

						{#if available.length > 0 && order.length < MAX_PARTICIPANTS}
							<div class="flex flex-wrap items-center gap-2">
								<span class="text-sm text-muted-foreground">Aggiungi:</span>
								{#each available as pilot (pilot.pilot_id)}
									<Button
										type="button"
										size="sm"
										variant="secondary"
										onclick={() => addToOrder(pilot.pilot_id)}
									>
										+ {pilot.pilot_name}
									</Button>
								{/each}
							</div>
						{/if}

						<div class="flex items-center gap-3">
							<Button type="submit" disabled={busy || order.length === 0}>
								{isRaceClosed ? 'Salva la correzione' : 'Chiudi la gara'}
							</Button>
							{#if saved}
								<span class="text-sm text-muted-foreground" role="status">Salvato.</span>
							{/if}
						</div>
						{#if saveError}
							<p class="text-sm text-destructive" role="alert">{saveError}</p>
						{/if}
					</form>
				</Card.Content>
			</Card.Root>
		{/if}
	{/if}
</main>
