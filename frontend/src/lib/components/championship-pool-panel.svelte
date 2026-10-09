<script lang="ts">
	import { onMount } from 'svelte';
	import { fetchShopPool, type ShopPool, type ShopPoolSection } from '$lib/shop-pool-api';
	import { errorMessage } from '$lib/shop-admin-format';

	// Pool complete del campionato: per ogni carta le copie rimaste e la probabilità.
	let { championshipId }: { championshipId: number } = $props();

	let pool = $state<ShopPool | null>(null);
	let error = $state<string | null>(null);

	function summary(data: ShopPoolSection): string {
		return `${data.cards.length} carte, ${data.total_copies} copie`;
	}

	function percent(value: number): string {
		return `${value.toLocaleString('it-IT', { maximumFractionDigits: 2 })}%`;
	}

	onMount(async () => {
		try {
			pool = await fetchShopPool(championshipId);
		} catch (e) {
			error = errorMessage(e);
		}
	});
</script>

{#snippet section(title: string, data: ShopPoolSection)}
	<section class="space-y-2">
		<h3 class="font-semibold">{title}</h3>
		<p class="text-sm text-muted-foreground">{summary(data)}</p>
		{#if data.cards.length === 0}
			<p class="text-sm text-muted-foreground">Nessuna carta.</p>
		{:else}
			<table class="w-full text-sm">
				<thead>
					<tr class="border-b text-left text-muted-foreground">
						<th class="py-1 font-normal">Carta</th>
						<th class="py-1 text-right font-normal">Copie</th>
						<th class="py-1 text-right font-normal">Probabilità</th>
					</tr>
				</thead>
				<tbody>
					{#each data.cards as card (card.path)}
						<tr class="border-b last:border-0">
							<td class="py-1">
								<div class="flex items-center gap-2">
									<img
										src={card.path}
										alt={card.name}
										loading="lazy"
										class="h-12 w-8 rounded object-cover"
									/>
									<span>{card.name}</span>
								</div>
							</td>
							<td class="py-1 text-right">{card.copies}</td>
							<td class="py-1 text-right">{percent(card.probability)}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{/if}
	</section>
{/snippet}

<div class="space-y-6">
	{#if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{:else if !pool}
		<p class="text-muted-foreground">Caricamento…</p>
	{:else}
		<p class="text-sm text-muted-foreground">
			Probabilità alla prima estrazione, senza filtro. Il filtro di un pacchetto la modifica.
		</p>
		{@render section('Modifiche', pool.modifiche)}
		{@render section('Sponsor', pool.sponsor)}
	{/if}
</div>
