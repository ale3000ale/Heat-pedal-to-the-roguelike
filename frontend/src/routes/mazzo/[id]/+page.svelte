<!-- frontend/src/routes/mazzo/[id]/+page.svelte -->
<!-- Dettaglio di un mazzo concreto: mostra le carte deserializzate dal JSON di Deck.cards. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { apiRequest } from '$lib/api';
	import DeckGrid from '$lib/components/DeckGrid.svelte';

	interface CardItem { path: string; value: number }
	interface DeckOut {
		id: number;
		pilot_name?: string | null;
		championship_name?: string | null;
		cards: CardItem[];
	}

	let deck: DeckOut | null = null;
	let loading = true;
	let errorMsg = '';

	// loadDeck(id)
	// id: id del mazzo estratto dal parametro di route.
	// Recupera il mazzo dal backend, che restituisce le carte gia' deserializzate dal JSON in DB.
	async function loadDeck(id: string): Promise<void> {
		loading = true;
		errorMsg = '';
		try {
			deck = await apiRequest<DeckOut>(`/decks/${id}`, { auth: true });
		} catch (e) {
			errorMsg = e instanceof Error ? e.message : 'Mazzo non trovato';
		} finally {
			loading = false;
		}
	}

	onMount(() => loadDeck($page.params.id));
</script>

<svelte:head><title>Heat - Dettaglio mazzo</title></svelte:head>

{#if loading}
	<p>Caricamento…</p>
{:else if errorMsg}
	<p class="text-racing-red">{errorMsg}</p>
{:else if deck}
	<h1 class="font-display text-2xl font-bold mb-2">Mazzo di {deck.pilot_name ?? 'sconosciuto'}</h1>
	{#if deck.championship_name}<p class="text-sm opacity-70 mb-6">Campionato: {deck.championship_name}</p>{/if}
	<DeckGrid cards={deck.cards} />
{/if}
