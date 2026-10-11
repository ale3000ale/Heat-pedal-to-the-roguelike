<script lang="ts">
	import { onMount } from 'svelte';
	import { fetchAllHistory } from '$lib/shop-api';
	import { errorMessage } from '$lib/shop-admin-format';
	import type { ShopHistory } from '$lib/shop-types';
	import ShopHistoryList from '$lib/components/shop-history-list.svelte';

	// Cronologia completa degli acquisti di un campionato (solo admin).
	let { championshipId }: { championshipId: number } = $props();

	let history = $state<ShopHistory | null>(null);
	let error = $state<string | null>(null);

	onMount(async () => {
		try {
			history = await fetchAllHistory(championshipId);
		} catch (e) {
			error = errorMessage(e);
		}
	});
</script>

{#if error}
	<p class="text-sm text-destructive" role="alert">{error}</p>
{:else if !history}
	<p class="text-muted-foreground">Caricamento…</p>
{:else}
	<div class="space-y-4">
		<ShopHistoryList {history} />
	</div>
{/if}
