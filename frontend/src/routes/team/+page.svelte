<!-- frontend/src/routes/team/+page.svelte -->
<!-- Pagina Team: senza login elenco ordinato per punti; con login solo i team dell'utente + creazione. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/store/auth';
	import { apiRequest } from '$lib/api';
	import TeamList from '$lib/components/TeamList.svelte';
	import NewTeamModal from '$lib/components/NewTeamModal.svelte';

	interface TeamOut {
		id: number;
		name: string;
		total_points: number;
		pilots: { id: number; name: string; point: number; is_current_user_pilot: boolean }[];
	}
	interface PilotOut {
		id: number;
		name: string;
		team: number | null;
	}

	let teams: TeamOut[] = [];
	let availablePilots: { id: number; name: string }[] = [];
	let modalOpen = false;
	let loading = true;
	let errorMsg = '';

	// loadTeams()
	// Nessun parametro.
	// Carica l'elenco team coerente con lo stato di login (globale ordinato per punti, oppure solo i propri).
	async function loadTeams(): Promise<void> {
		loading = true;
		errorMsg = '';
		try {
			teams = await apiRequest<TeamOut[]>('/teams', { auth: !!$authStore.token });
			if ($authStore.token) {
				const pilots = await apiRequest<PilotOut[]>('/pilots', { auth: true });
				availablePilots = pilots.filter((p) => p.team === null).map((p) => ({ id: p.id, name: p.name }));
			}
		} catch (e) {
			errorMsg = e instanceof Error ? e.message : 'Errore nel caricamento dei team';
		} finally {
			loading = false;
		}
	}

	// handleTeamCreated()
	// Nessun parametro.
	// Chiude la modale e ricarica l'elenco team dopo una creazione riuscita.
	function handleTeamCreated(): void {
		modalOpen = false;
		loadTeams();
	}

	onMount(loadTeams);
</script>

<svelte:head><title>Heat - Team</title></svelte:head>

<div class="flex justify-between items-center mb-6">
	<h1 class="font-display text-2xl font-bold">Team</h1>
	{#if $authStore.token}
		<button class="btn-primary" on:click={() => (modalOpen = true)}>Nuovo team</button>
	{/if}
</div>

{#if loading}
	<p>Caricamento…</p>
{:else if errorMsg}
	<p class="text-racing-red">{errorMsg}</p>
{:else}
	<TeamList {teams} />
{/if}

<NewTeamModal
	open={modalOpen}
	{availablePilots}
	on:created={handleTeamCreated}
	on:close={() => (modalOpen = false)}
/>
