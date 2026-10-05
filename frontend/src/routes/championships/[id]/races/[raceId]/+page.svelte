<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { api } from '$lib/api';
	import type { Pilot } from '$lib/types';
	import type { RaceDetail } from '$lib/race-types';
	import * as Card from '$lib/components/ui/card';

	let race = $state<RaceDetail | null>(null);
	let myPilots = $state<Pilot[]>([]);
	let error = $state<string | null>(null);

	let myIds = $derived(new Set(myPilots.map((p) => p.id)));

	// La data della gara può non essere impostata.
	function raceDate(value: string | null): string {
		return value ? new Date(value).toLocaleDateString('it-IT') : 'Data da definire';
	}

	onMount(async () => {
		try {
			[race, myPilots] = await Promise.all([
				api<RaceDetail>(`/championships/${page.params.id}/races/${page.params.raceId}`),
				api<Pilot[]>('/pilots')
			]);
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
				{race.participants === 1 ? 'partecipante' : 'partecipanti'}
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
								<span class="text-sm">{result.points} punti</span>
							</li>
						{/each}
					</ol>
				{/if}
			</Card.Content>
		</Card.Root>
	{/if}
</main>
