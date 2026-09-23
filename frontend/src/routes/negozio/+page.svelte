<!-- frontend/src/routes/negozio/+page.svelte -->
<!-- Pagina Negozio: senza login solo elenco oggetti/prezzi; con login elenco campionati -> negozio specifico. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { authStore } from '$lib/store/auth';
	import { apiRequest } from '$lib/api';
	import ShopItemCard from '$lib/components/ShopItemCard.svelte';

	interface ShopItemOut {
		id: number; championship_id: number; name: string; description?: string | null;
		price_gold: number; price_points: number; requirements?: string | null;
	}
	interface ChampionshipOut { id: number; name: string; date: string }

	let publicItems: ShopItemOut[] = [];
	let championships: ChampionshipOut[] = [];
	let loading = true;
	let errorMsg = '';

	// loadData()
	// Nessun parametro.
	// Senza login carica tutti gli oggetti (solo consultazione); con login carica l'elenco campionati
	// da cui l'utente sceglie il negozio specifico da aprire.
	async function loadData(): Promise<void> {
		loading = true;
		errorMsg = '';
		try {
			if ($authStore.token) {
				championships = await apiRequest<ChampionshipOut[]>('/championships');
			} else {
				publicItems = await apiRequest<ShopItemOut[]>('/shop/public');
			}
		} catch (e) {
			errorMsg = e instanceof Error ? e.message : 'Errore nel caricamento del negozio';
		} finally {
			loading = false;
		}
	}

	onMount(loadData);
</script>

<svelte:head><title>Heat - Negozio</title></svelte:head>

<h1 class="font-display text-2xl font-bold mb-6">Negozio</h1>

{#if loading}
	<p>Caricamento…</p>
{:else if errorMsg}
	<p class="text-racing-red">{errorMsg}</p>
{:else if $authStore.token}
	<p class="mb-4 text-sm opacity-70">Seleziona un campionato per accedere al relativo negozio.</p>
	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		{#each championships as champ}
			<a href={`/negozio/${champ.id}`} class="app-card block">
				<h2 class="font-semibold">{champ.name}</h2>
				<p class="text-sm opacity-70">{new Date(champ.date).toLocaleDateString('it-IT')}</p>
			</a>
		{/each}
	</div>
{:else}
	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		{#each publicItems as item}
			<ShopItemCard {item} purchasable={false} />
		{/each}
		{#if publicItems.length === 0}<p class="text-sm opacity-70">Nessun oggetto disponibile.</p>{/if}
	</div>
{/if}
