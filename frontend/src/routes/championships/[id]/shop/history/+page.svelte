<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { fetchOwnHistory } from '$lib/shop-api';
	import type { ShopHistory } from '$lib/shop-types';
	import ShopHistoryList from '$lib/components/shop-history-list.svelte';

	const championshipId = Number(page.params.id);

	let history = $state<ShopHistory | null>(null);
	let error = $state<string | null>(null);

	onMount(async () => {
		try {
			history = await fetchOwnHistory(championshipId);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		}
	});
</script>

<svelte:head><title>Storico acquisti - Heat</title></svelte:head>

<main class="mx-auto max-w-3xl space-y-6 p-6">
	<a
		href={resolve('/championships/[id]/shop', { id: String(championshipId) })}
		class="text-sm text-muted-foreground hover:text-foreground"
	>
		← Negozio
	</a>

	<h1 class="text-2xl font-bold">Storico acquisti</h1>

	{#if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{:else if !history}
		<p class="text-muted-foreground">Caricamento…</p>
	{:else}
		<ShopHistoryList {history} />
	{/if}
</main>
