<!-- frontend/src/routes/piloti/[id]/+page.svelte -->
<!-- Pagina dettaglio pilota: statistiche complete (gold, sponsor, punti, team, campionato). -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { apiRequest } from '$lib/api';

	interface PilotOut {
		id: number;
		name: string;
		gold: number;
		sponsor: number;
		point: number;
		team_name?: string | null;
		championship_name?: string | null;
	}

	let pilot: PilotOut | null = null;
	let loading = true;
	let errorMsg = '';

	// loadPilot(id)
	// id: id del pilota estratto dal parametro di route.
	// Carica il dettaglio completo del pilota dall'API per mostrarlo nella pagina dedicata.
	async function loadPilot(id: string): Promise<void> {
		loading = true;
		errorMsg = '';
		try {
			pilot = await apiRequest<PilotOut>(`/pilots/${id}`);
		} catch (e) {
			errorMsg = e instanceof Error ? e.message : 'Pilota non trovato';
		} finally {
			loading = false;
		}
	}

	onMount(() => loadPilot($page.params.id));
</script>

<svelte:head><title>Heat - Pilota</title></svelte:head>

{#if loading}
	<p>Caricamento…</p>
{:else if errorMsg}
	<p class="text-racing-red">{errorMsg}</p>
{:else if pilot}
	<div class="app-card max-w-lg">
		<h1 class="font-display text-2xl font-bold mb-4">{pilot.name}</h1>
		<div class="speed-indicator mb-4"></div>
		<dl class="grid grid-cols-2 gap-3 text-sm">
			<dt class="opacity-70">Punti</dt><dd class="font-semibold">{pilot.point}</dd>
			<dt class="opacity-70">Gold</dt><dd class="font-semibold">{pilot.gold}</dd>
			<dt class="opacity-70">Sponsor</dt><dd class="font-semibold">{pilot.sponsor}</dd>
			<dt class="opacity-70">Team</dt><dd class="font-semibold">{pilot.team_name ?? 'Nessuno'}</dd>
			<dt class="opacity-70">Campionato</dt><dd class="font-semibold">{pilot.championship_name ?? 'Nessuno'}</dd>
		</dl>
	</div>
{/if}
