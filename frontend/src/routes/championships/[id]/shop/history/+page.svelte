<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { fetchOwnHistory } from '$lib/shop-api';
	import { cardSummary, purchaseLine } from '$lib/shop-format';
	import type { ShopHistory } from '$lib/shop-types';

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
	{:else if history.pilots.length === 0}
		<p class="text-sm text-muted-foreground">Nessun acquisto.</p>
	{:else}
		{#each history.pilots as pilot (pilot.pilot_id ?? pilot.pilot_name)}
			<section class="space-y-3">
				<h2 class="text-lg font-semibold">{pilot.pilot_name}</h2>
				{#if pilot.purchases.length === 0}
					<p class="text-sm text-muted-foreground">Nessun acquisto.</p>
				{:else}
					<ul class="space-y-2">
						{#each pilot.purchases as purchase (purchase.id)}
							<li class="rounded-lg border bg-card p-3 text-sm">
								<div class="flex flex-wrap items-center justify-between gap-2">
									<span class="font-medium">{purchase.pack_name}</span>
									<span class="text-muted-foreground">{purchaseLine(purchase)}</span>
								</div>
								<div class="mt-2 space-y-1 text-muted-foreground">
									<p>Modifiche: {cardSummary(purchase.cards_modifiche)}</p>
									<p>Sponsor: {cardSummary(purchase.cards_sponsor)}</p>
								</div>
							</li>
						{/each}
					</ul>
				{/if}
			</section>
		{/each}
	{/if}
</main>
