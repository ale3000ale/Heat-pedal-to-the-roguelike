<!-- frontend/src/routes/mazzo/+page.svelte -->
<!-- Pagina Mazzo: senza login mostra tutte le carte del gioco (prototipi); con login elenco mazzi + ricerca. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/store/auth';
	import { apiRequest } from '$lib/api';
	import DeckGrid from '$lib/components/DeckGrid.svelte';
	import SearchBar from '$lib/components/SearchBar.svelte';

	interface CardItem { path: string; value: number }
	interface DeckPrototypeOut { id: number; name: string; cards: CardItem[] }
	interface DeckOut { id: number; pilot_name?: string | null; championship_name?: string | null; cards: CardItem[] }

	let prototypes: DeckPrototypeOut[] = [];
	let decks: DeckOut[] = [];
	let loading = true;
	let errorMsg = '';

	let searchValues: Record<string, string> = { search_pilot: '', search_championship: '' };
	const searchFields = [
		{ key: 'search_pilot', label: 'Pilota' },
		{ key: 'search_championship', label: 'Campionato' }
	];

	// buildQuery(values)
	// values: filtri di ricerca correnti per pilota/campionato.
	// Costruisce la query string per l'endpoint /decks, omettendo i campi vuoti.
	function buildQuery(values: Record<string, string>): string {
		const params = new URLSearchParams();
		for (const [k, v] of Object.entries(values)) if (v) params.set(k, v);
		const qs = params.toString();
		return qs ? `?${qs}` : '';
	}

	// loadData()
	// Nessun parametro.
	// Carica tutte le carte del gioco (anonimo) oppure i mazzi dell'utente filtrabili (loggato).
	async function loadData(): Promise<void> {
		loading = true;
		errorMsg = '';
		try {
			if ($authStore.token) {
				decks = await apiRequest<DeckOut[]>(`/decks${buildQuery(searchValues)}`, { auth: true });
			} else {
				prototypes = await apiRequest<DeckPrototypeOut[]>('/decks/prototypes');
			}
		} catch (e) {
			errorMsg = e instanceof Error ? e.message : 'Errore nel caricamento dei mazzi';
		} finally {
			loading = false;
		}
	}

	// handleSearch(event)
	// event.detail: filtri correnti dal componente SearchBar.
	// Aggiorna i filtri e ricarica l'elenco mazzi dell'utente.
	function handleSearch(event: CustomEvent<Record<string, string>>): void {
		searchValues = event.detail;
		loadData();
	}

	onMount(loadData);
</script>

<svelte:head><title>Heat - Mazzo</title></svelte:head>

<h1 class="font-display text-2xl font-bold mb-6">Mazzo</h1>

{#if $authStore.token}
	<SearchBar fields={searchFields} values={searchValues} on:search={handleSearch} />
{/if}

{#if loading}
	<p>Caricamento…</p>
{:else if errorMsg}
	<p class="text-racing-red">{errorMsg}</p>
{:else if $authStore.token}
	<div class="space-y-6">
		{#each decks as deck}
			<div>
				<h2 class="font-display font-semibold text-lg mb-2">
					<a href={`/mazzo/${deck.id}`} class="hover:text-racing-red">
						Mazzo di {deck.pilot_name ?? 'sconosciuto'}
					</a>
					{#if deck.championship_name}<span class="text-sm opacity-70"> · {deck.championship_name}</span>{/if}
				</h2>
			</div>
		{/each}
		{#if decks.length === 0}<p class="text-sm opacity-70">Nessun mazzo trovato.</p>{/if}
	</div>
{:else}
	{#each prototypes as proto}
		<h2 class="font-display font-semibold text-lg mb-3 mt-6">{proto.name}</h2>
		<DeckGrid cards={proto.cards} />
	{/each}
{/if}
