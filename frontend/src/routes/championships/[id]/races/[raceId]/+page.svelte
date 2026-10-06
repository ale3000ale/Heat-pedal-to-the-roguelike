<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { beforeNavigate, goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { api } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import type { ChampionshipDetail, Pilot } from '$lib/types';
	import type { RaceDetail } from '$lib/race-types';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';

	// Una riga della classifica: un pilota in ordine di arrivo con i suoi punti sponsor.
	interface Row {
		pilot_id: number;
		name: string;
		sponsor: number;
	}

	// Un pilota dichiarato a mano come non partecipante.
	interface Absent {
		pilot_id: number;
		name: string;
	}

	const MAX_PARTICIPANTS = 12;
	const inputClass =
		'h-8 w-20 rounded-md border border-input bg-background px-2 text-sm disabled:opacity-50';

	let race = $state<RaceDetail | null>(null);
	let championship = $state<ChampionshipDetail | null>(null);
	let myPilots = $state<Pilot[]>([]);
	let order = $state<Row[]>([]);
	let absent = $state<Absent[]>([]);
	let error = $state<string | null>(null);
	let saveError = $state<string | null>(null);
	let saved = $state(false);
	let busy = $state(false);
	let leaveTarget = $state<URL | null>(null);
	let allowLeave = false;

	let myIds = $derived(new Set(myPilots.map((p) => p.id)));
	// Una gara con almeno un risultato è terminata, altrimenti è in corso.
	let isRaceClosed = $derived(race !== null && race.participants > 0);
	// Il giudice può terminare una gara in corso; solo l'admin può correggerne una terminata.
	// Un campionato chiuso è in sola lettura per tutti.
	let canEdit = $derived(
		championship !== null &&
			!championship.is_closed &&
			auth.canManageRaces &&
			(!isRaceClosed || auth.canCorrectRaces)
	);
	// Iscritti non ancora assegnati né alla classifica né ai non partecipanti.
	let available = $derived(
		race
			? race.results.filter(
					(r) =>
						!order.some((row) => row.pilot_id === r.pilot_id) &&
						!absent.some((a) => a.pilot_id === r.pilot_id)
				)
			: []
	);
	// Si può terminare solo con almeno un pilota in classifica e tutti gli altri dichiarati.
	let canFinish = $derived(order.length > 0 && available.length === 0);
	// Uscire dalla pagina con una classifica non salvata chiede conferma.
	let needsGuard = $derived(canEdit && !isRaceClosed && order.length > 0);

	// La data può mancare nelle gare create prima della data automatica.
	function raceDate(value: string | null): string {
		return value ? new Date(value).toLocaleDateString('it-IT') : 'Data da definire';
	}

	// Riempie il modulo con i dati già registrati: classifica in ordine di arrivo e,
	// se la gara è terminata, chi non ha partecipato.
	function loadOrder(detail: RaceDetail) {
		order = detail.results
			.filter((r) => r.position !== null)
			.map((r) => ({ pilot_id: r.pilot_id, name: r.pilot_name, sponsor: r.sponsor_points }));
		absent =
			detail.participants > 0
				? detail.results
						.filter((r) => r.position === null)
						.map((r) => ({ pilot_id: r.pilot_id, name: r.pilot_name }))
				: [];
	}

	function addToOrder(pilotId: number) {
		const found = race?.results.find((r) => r.pilot_id === pilotId);
		if (!found || order.length >= MAX_PARTICIPANTS) return;
		order.push({ pilot_id: found.pilot_id, name: found.pilot_name, sponsor: 0 });
	}

	function removeFromOrder(index: number) {
		order.splice(index, 1);
	}

	function addToAbsent(pilotId: number) {
		const found = race?.results.find((r) => r.pilot_id === pilotId);
		if (!found) return;
		absent.push({ pilot_id: found.pilot_id, name: found.pilot_name });
	}

	function removeFromAbsent(index: number) {
		absent.splice(index, 1);
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
		if (!canFinish) return;
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
						})),
						absent: absent.map((a) => a.pilot_id)
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

	// Con una classifica non terminata blocca l'uscita: nella navigazione interna mostra
	// il popup, in chiusura/ricarica della scheda usa l'avviso del browser.
	beforeNavigate(({ cancel, to, willUnload }) => {
		if (allowLeave || !needsGuard) return;
		cancel();
		if (!willUnload && to) leaveTarget = to.url;
	});

	async function confirmLeave() {
		const target = leaveTarget;
		leaveTarget = null;
		if (!target) return;
		allowLeave = true;
		// eslint-disable-next-line svelte/no-navigation-without-resolve
		await goto(target.pathname + target.search + target.hash);
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
				{#if isRaceClosed}
					<span class="font-medium text-green-600">terminata</span>
				{:else}
					<span class="font-medium text-red-600">in corso</span>
				{/if}
			</p>
		</div>

		{#if isRaceClosed || !canEdit}
			<Card.Root>
				<Card.Header>
					<Card.Title>Risultati</Card.Title>
					<Card.Description>Chi non ha partecipato ha 0 punti.</Card.Description>
				</Card.Header>
				<Card.Content>
					{#if !isRaceClosed}
						<p class="text-sm text-muted-foreground">Gara in corso: nessun risultato registrato.</p>
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
		{/if}

		{#if canEdit}
			<Card.Root>
				<Card.Header>
					<Card.Title>{isRaceClosed ? 'Correggi i risultati' : 'Termina la gara'}</Card.Title>
					<Card.Description>
						Metti in classifica i piloti in ordine di arrivo (massimo {MAX_PARTICIPANTS}) con i punti
						sponsor di ciascuno, e indica a mano chi non partecipa. Ogni iscritto va assegnato. Gli
						sponsor vengono assegnati al salvataggio.
					</Card.Description>
				</Card.Header>
				<Card.Content class="space-y-4">
					<form onsubmit={save} class="space-y-4">
						<h2 class="text-sm font-semibold">Classifica</h2>
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

						{#if available.length > 0}
							<div class="space-y-2">
								<h2 class="text-sm font-semibold">Da assegnare</h2>
								{#each available as pilot (pilot.pilot_id)}
									<div class="flex flex-wrap items-center gap-2">
										<span class="min-w-32 flex-1 text-sm font-medium">{pilot.pilot_name}</span>
										<Button
											type="button"
											size="sm"
											variant="secondary"
											disabled={order.length >= MAX_PARTICIPANTS}
											onclick={() => addToOrder(pilot.pilot_id)}
										>
											In classifica
										</Button>
										<Button
											type="button"
											size="sm"
											variant="outline"
											onclick={() => addToAbsent(pilot.pilot_id)}
											aria-label={`${pilot.pilot_name} non partecipa`}
										>
											Non partecipa
										</Button>
									</div>
								{/each}
							</div>
						{/if}

						{#if absent.length > 0}
							<div class="space-y-2">
								<h2 class="text-sm font-semibold">Non partecipano</h2>
								{#each absent as a, index (a.pilot_id)}
									<div class="flex flex-wrap items-center gap-2">
										<span class="min-w-32 flex-1 text-sm font-medium">{a.name}</span>
										<Button
											type="button"
											size="sm"
											variant="ghost"
											onclick={() => removeFromAbsent(index)}
											aria-label={`Rimetti ${a.name} da assegnare`}
										>
											Rimetti
										</Button>
									</div>
								{/each}
							</div>
						{/if}

						<div class="flex flex-wrap items-center gap-3">
							<Button type="submit" disabled={busy || !canFinish}>
								{isRaceClosed ? 'Salva la correzione' : 'Termina'}
							</Button>
							{#if available.length > 0}
								<span class="text-sm text-muted-foreground">
									Assegna tutti i piloti: in classifica o tra chi non partecipa.
								</span>
							{:else if order.length === 0}
								<span class="text-sm text-muted-foreground">
									Serve almeno un pilota in classifica.
								</span>
							{/if}
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

{#if leaveTarget}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
		role="dialog"
		aria-modal="true"
		aria-label="Uscire senza terminare la gara?"
	>
		<div class="w-full max-w-sm space-y-4 rounded-lg border bg-background p-6 shadow-lg">
			<h2 class="text-lg font-semibold">Uscire senza terminare la gara?</h2>
			<p class="text-sm text-muted-foreground">
				La classifica non è stata salvata: se esci la gara resta in corso e perdi le modifiche.
			</p>
			<div class="flex justify-end gap-2">
				<Button variant="destructive" onclick={confirmLeave}>Esci</Button>
				<Button variant="outline" onclick={() => (leaveTarget = null)}>Rimani</Button>
			</div>
		</div>
	</div>
{/if}
