<!-- frontend/src/routes/+page.svelte -->
<!-- Home: senza login mostra la classifica dell'ultimo campionato; con login mostra i top 3 piloti
     dell'utente e l'ultimo campionato in cui hanno partecipato. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/store/auth';
	import { apiRequest } from '$lib/api';
	import PilotCard from '$lib/components/PilotCard.svelte';

	interface Participant {
		pilot_id: number;
		pilot_name: string;
		points: number;
		ranking: number | null;
	}
	interface ChampionshipOut {
		id: number;
		name: string;
		date: string;
		participants: Participant[];
	}
	interface PilotOut {
		id: number;
		name: string;
		point: number;
		championship_name?: string | null;
	}

	let championship: ChampionshipOut | null = null;
	let topPilots: PilotOut[] = [];
	let loading = true;
	let errorMsg = '';

	// loadHomeData()
	// Nessun parametro.
	// Carica i dati della Home a seconda dello stato di login: campionato piu' recente (globale o
	// dell'utente) e, se loggato, i top 3 piloti per punteggio.
	async function loadHomeData(): Promise<void> {
		loading = true;
		errorMsg = '';
		try {
			const isLoggedIn = !!$authStore.token;
			championship = await apiRequest<ChampionshipOut | null>('/championships/home', {
				auth: isLoggedIn
			});
			if (isLoggedIn) {
				const pilots = await apiRequest<PilotOut[]>('/pilots', { auth: true });
				topPilots = [...pilots].sort((a, b) => b.point - a.point).slice(0, 3);
			}
		} catch (e) {
			errorMsg = e instanceof Error ? e.message : 'Errore nel caricamento della Home';
		} finally {
			loading = false;
		}
	}

	onMount(loadHomeData);
</script>

<svelte:head><title>Heat - Home</title></svelte:head>

<h1 class="font-display text-3xl font-bold mb-2">Heat</h1>
<div class="speed-indicator mb-6"></div>

{#if loading}
	<p>Caricamento…</p>
{:else if errorMsg}
	<p class="text-racing-red">{errorMsg}</p>
{:else}
	{#if $authStore.token}
		<h2 class="font-display text-xl font-semibold mb-3">I tuoi migliori piloti</h2>
		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 mb-8">
			{#each topPilots as pilot}
				<PilotCard {pilot} championshipName={pilot.championship_name ?? '—'} />
			{/each}
			{#if topPilots.length === 0}
				<p class="text-sm opacity-70">Non hai ancora piloti con punteggio.</p>
			{/if}
		</div>
	{/if}

	<h2 class="font-display text-xl font-semibold mb-3">
		{$authStore.token ? 'Ultimo campionato con tuoi piloti' : 'Ultimo campionato'}
	</h2>

	{#if championship}
		<div class="app-card">
			<h3 class="font-semibold text-lg mb-2">{championship.name}</h3>
			<p class="text-sm opacity-70 mb-3">{new Date(championship.date).toLocaleDateString('it-IT')}</p>
			<ol class="space-y-1">
				{#each championship.participants as p, i}
					<li class="flex justify-between border-b border-racing-silver/20 py-1">
						<span>{i + 1}. {p.pilot_name}</span>
						<span class="font-semibold">{p.points} pt</span>
					</li>
				{/each}
			</ol>
		</div>
	{:else}
		<p class="text-sm opacity-70">Nessun campionato disponibile.</p>
	{/if}
{/if}
