<script lang="ts">
	import { cardSummary, purchaseLine } from '$lib/shop-format';
	import type { ShopHistory } from '$lib/shop-types';

	// Storico degli acquisti diviso per pilota: usato dalla pagina del giocatore
	// e dal popup dell'admin.
	let { history }: { history: ShopHistory } = $props();
</script>

{#if history.pilots.length === 0}
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
