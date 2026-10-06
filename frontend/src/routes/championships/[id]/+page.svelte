<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { api } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import { standingKey } from '$lib/standings';
	import type { ChampionshipDetail, Pilot } from '$lib/types';
	import type { Race, Standing } from '$lib/race-types';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import GoldRulesForm from '$lib/components/gold-rules-form.svelte';
	import SettingsDialog from '$lib/components/settings-dialog.svelte';

	const selectClass =
		'h-8 rounded-md border border-input bg-background px-2 text-sm disabled:opacity-50';

	let championship = $state<ChampionshipDetail | null>(null);
	let standings = $state<Standing[]>([]);
	let races = $state<Race[]>([]);
	let myPilots = $state<Pilot[]>([]);
	let error = $state<string | null>(null);
	let actionError = $state<string | null>(null);
	let raceError = $state<string | null>(null);
	let busy = $state(false);
	let selectedPilot = $state('');
	let settingsOpen = $state(false);

	let myIds = $derived(new Set(myPilots.map((p) => p.id)));
	// Piloti che hanno un team e non sono già iscritti a questo campionato.
	let candidates = $derived(
		myPilots.filter(
			(p) => p.team_id !== null && !championship?.pilots.some((entrant) => entrant.id === p.id)
		)
	);

	// La data della gara può non essere impostata.
	function raceDate(value: string | null): string {
		return value ? new Date(value).toLocaleDateString('it-IT') : 'Data da definire';
	}

	// Ricarica i dati del campionato che cambiano dopo un'iscrizione.
	async function reload() {
		[championship, standings] = await Promise.all([
			api<ChampionshipDetail>(`/championships/${page.params.id}`),
			api<Standing[]>(`/championships/${page.params.id}/standings`)
		]);
	}

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

	async function enroll(event: SubmitEvent) {
		event.preventDefault();
		if (selectedPilot === '') return;
		actionError = null;
		busy = true;
		try {
			await api(`/championships/${page.params.id}/pilots`, {
				method: 'POST',
				body: { pilot_id: Number(selectedPilot) }
			});
			selectedPilot = '';
			await reload();
		} catch (e) {
			actionError = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			busy = false;
		}
	}

	// Admin e giudice: crea la prossima gara e apre subito la sua pagina per i risultati.
	async function createRace() {
		raceError = null;
		busy = true;
		try {
			const created = await api<Race>(`/championships/${page.params.id}/races`, {
				method: 'POST'
			});
			await goto(
				resolve('/championships/[id]/races/[raceId]', {
					id: String(page.params.id),
					raceId: String(created.id)
				})
			);
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

		{#if !championship.is_closed}
			<Card.Root>
				<Card.Header>
					<Card.Title>Iscrivi un tuo pilota</Card.Title>
					<Card.Description>
						Il pilota deve avere un team e non essere in un altro campionato attivo. L'iscrizione lo
						reimposta.
					</Card.Description>
				</Card.Header>
				<Card.Content>
					{#if candidates.length === 0}
						<p class="text-sm text-muted-foreground">Nessun tuo pilota può essere iscritto.</p>
					{:else}
						<form onsubmit={enroll} class="flex flex-wrap items-center gap-2">
							<select
								class={selectClass}
								bind:value={selectedPilot}
								required
								aria-label="Pilota da iscrivere"
							>
								<option value="">Scegli un pilota</option>
								{#each candidates as p (p.id)}
									<option value={String(p.id)}>{p.name}</option>
								{/each}
							</select>
							<Button type="submit" size="sm" disabled={busy || selectedPilot === ''}>
								Iscrivi
							</Button>
						</form>
					{/if}
					{#if actionError}
						<p class="mt-3 text-sm text-destructive" role="alert">{actionError}</p>
					{/if}
				</Card.Content>
			</Card.Root>
		{/if}

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
							<li class="flex items-center gap-3 py-2">
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
							</li>
						{/each}
					</ol>
				{/if}
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Header>
				<Card.Title>Gare</Card.Title>
				<Card.Description>{races.length} gare in calendario</Card.Description>
			</Card.Header>
			<Card.Content>
				{#if auth.canManageRaces && !championship.is_closed}
					<div class="mb-4">
						<Button size="sm" onclick={createRace} disabled={busy}>Nuova gara</Button>
						{#if raceError}
							<p class="mt-3 text-sm text-destructive" role="alert">{raceError}</p>
						{/if}
					</div>
				{/if}
				{#if races.length === 0}
					<p class="text-sm text-muted-foreground">Nessuna gara ancora disputata.</p>
				{:else}
					<ul class="divide-y">
						{#each races as race (race.id)}
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
									<span class="text-sm text-muted-foreground">
										{race.participants}
										{race.participants === 1 ? 'partecipante' : 'partecipanti'}
									</span>
								</a>
							</li>
						{/each}
					</ul>
				{/if}
			</Card.Content>
		</Card.Root>

		{#if auth.isAdmin}
			<SettingsDialog bind:open={settingsOpen} title="Impostazioni del campionato">
				<GoldRulesForm
					url={`/championships/${championship.id}/gold-rules`}
					title="Oro per gara"
					description="Oro dato a tutti gli iscritti dopo ogni gara, anche a chi non corre. Un totale negativo diventa 0. Le modifiche valgono dalla gara successiva."
					editable={!championship.is_closed}
				/>
			</SettingsDialog>
		{/if}
	{/if}
</main>
