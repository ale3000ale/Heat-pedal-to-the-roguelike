<!-- frontend/src/routes/piloti/+page.svelte -->
<!-- Pagina Piloti: senza login due elenchi (tutti / senza team); con login schede utente + ricerca + creazione. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/store/auth';
	import { apiRequest } from '$lib/api';
	import PilotList from '$lib/components/PilotList.svelte';
	import SearchBar from '$lib/components/SearchBar.svelte';
	import NewPilotModal from '$lib/components/NewPilotModal.svelte';

	interface PilotOut {
		id: number;
		name: string;
		point: number;
		team_name?: string | null;
		championship_name?: string | null;
	}

	let allPilots: PilotOut[] = [];
	let pilotsNoTeam: PilotOut[] = [];
	let modalOpen = false;
	let loading = true;
	let errorMsg = '';

	let searchValues: Record<string, string> = { search_name: '', search_team: '', search_championship: '' };

	const searchFields = [
		{ key: 'search_name', label: 'Nome pilota' },
		{ key: 'search_team', label: 'Team' },
		{ key: 'search_championship', label: 'Campionato' }
	];

	// buildQuery(values)
	// values: dizionario chiave->valore dei filtri di ricerca correnti.
	// Costruisce la query string per l'endpoint /pilots, omettendo i campi vuoti.
	function buildQuery(values: Record<string, string>): string {
		const params = new URLSearchParams();
		for (const [k, v] of Object.entries(values)) if (v) params.set(k, v);
		const qs = params.toString();
		return qs ? `?${qs}` : '';
	}

	// loadPilots()
	// Nessun parametro.
	// Carica i piloti in base allo stato di login: tutti + senza team (anonimo), oppure solo i propri (loggato).
	async function loadPilots(): Promise<void> {
		loading = true;
		errorMsg = '';
		try {
			if ($authStore.token) {
				allPilots = await apiRequest<PilotOut[]>(`/pilots${buildQuery(searchValues)}`, { auth: true });
			} else {
				allPilots = await apiRequest<PilotOut[]>('/pilots');
				pilotsNoTeam = await apiRequest<PilotOut[]>('/pilots/without-team');
			}
		} catch (e) {
			errorMsg = e instanceof Error ? e.message : 'Errore nel caricamento dei piloti';
		} finally {
			loading = false;
		}
	}

	// handleSearch(event)
	// event.detail: filtri correnti inviati dal componente SearchBar.
	// Aggiorna i valori di ricerca e ricarica l'elenco piloti filtrato (solo vista "con login").
	function handleSearch(event: CustomEvent<Record<string, string>>): void {
		searchValues = event.detail;
		loadPilots();
	}

	onMount(loadPilots);
</script>

<svelte:head><title>Heat - Piloti</title></svelte:head>

<div class="flex justify-between items-center mb-6">
	<h1 class="font-display text-2xl font-bold">Piloti</h1>
	{#if $authStore.token}
		<button class="btn-primary" on:click={() => (modalOpen = true)}>Nuovo pilota</button>
	{/if}
</div>

{#if $authStore.token}
	<SearchBar fields={searchFields} values={searchValues} on:search={handleSearch} />
{/if}

{#if loading}
	<p>Caricamento…</p>
{:else if errorMsg}
	<p class="text-racing-red">{errorMsg}</p>
{:else if $authStore.token}
	<PilotList pilots={allPilots} emptyMessage="Non hai ancora piloti." />
{:else}
	<div class="grid gap-6 sm:grid-cols-2">
		<div>
			<h2 class="font-display font-semibold text-lg mb-3">Tutti i piloti</h2>
			<PilotList pilots={allPilots} />
		</div>
		<div>
			<h2 class="font-display font-semibold text-lg mb-3">Piloti senza team</h2>
			<PilotList pilots={pilotsNoTeam} emptyMessage="Tutti i piloti hanno un team." />
		</div>
	</div>
{/if}

<NewPilotModal open={modalOpen} on:created={() => { modalOpen = false; loadPilots(); }} on:close={() => (modalOpen = false)} />
