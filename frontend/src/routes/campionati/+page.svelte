<!-- frontend/src/routes/campionati/+page.svelte -->
<!-- Pagina Campionati: panoramica di tutti i campionati con relativa classifica partecipanti. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { apiRequest } from '$lib/api';

	interface Participant { pilot_id: number; pilot_name: string; points: number }
	interface ChampionshipOut { id: number; name: string; date: string; participants: Participant[] }

	let championships: ChampionshipOut[] = [];
	let loading = true;
	let errorMsg = '';

	// loadChampionships()
	// Nessun parametro.
	// Carica tutti i campionati ordinati per data (dal piu' recente), con relativa classifica.
	async function loadChampionships(): Promise<void> {
		loading = true;
		errorMsg = '';
		try {
			championships = await apiRequest<ChampionshipOut[]>('/championships');
		} catch (e) {
			errorMsg = e instanceof Error ? e.message : 'Errore nel caricamento dei campionati';
		} finally {
			loading = false;
		}
	}

	onMount(loadChampionships);
</script>

<svelte:head><title>Heat - Campionati</title></svelte:head>

<h1 class="font-display text-2xl font-bold mb-6">Campionati</h1>

{#if loading}
	<p>Caricamento…</p>
{:else if errorMsg}
	<p class="text-racing-red">{errorMsg}</p>
{:else}
	<div class="space-y-6">
		{#each championships as champ}
			<div class="app-card">
				<div class="flex justify-between items-baseline mb-3">
					<h2 class="font-display font-semibold text-lg">{champ.name}</h2>
					<span class="text-sm opacity-70">{new Date(champ.date).toLocaleDateString('it-IT')}</span>
				</div>
				<ol class="space-y-1">
					{#each champ.participants as p, i}
						<li class="flex justify-between border-b border-racing-silver/20 py-1">
							<span>{i + 1}. {p.pilot_name}</span>
							<span class="font-semibold">{p.points} pt</span>
						</li>
					{/each}
					{#if champ.participants.length === 0}
						<p class="text-sm opacity-70">Nessun partecipante registrato.</p>
					{/if}
				</ol>
			</div>
		{/each}
		{#if championships.length === 0}<p class="text-sm opacity-70">Nessun campionato disponibile.</p>{/if}
	</div>
{/if}
