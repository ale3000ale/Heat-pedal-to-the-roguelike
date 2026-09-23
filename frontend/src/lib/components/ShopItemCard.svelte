<!-- frontend/src/lib/components/ShopItemCard.svelte -->
<!-- Card di un oggetto del negozio: prezzo, descrizione, requisiti, bottone acquisto opzionale. -->
<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let item: {
		id: number;
		name: string;
		description?: string | null;
		price_gold: number;
		price_points: number;
		requirements?: string | null;
	};
	export let purchasable = false; // true solo nella vista "con login" dentro un campionato specifico
	export let disabled = false; // true se il pilota non ha fondi sufficienti

	const dispatch = createEventDispatcher<{ buy: number }>();
</script>

<div class="app-card flex flex-col justify-between">
	<div>
		<h3 class="font-display font-semibold text-lg">{item.name}</h3>
		{#if item.description}<p class="text-sm opacity-70 mt-1">{item.description}</p>{/if}
		{#if item.requirements}<p class="text-xs opacity-60 mt-1">Requisiti: {item.requirements}</p>{/if}
	</div>
	<div class="flex justify-between items-center mt-4">
		<span class="text-sm font-semibold">
			{item.price_gold} gold{#if item.price_points} · {item.price_points} pt{/if}
		</span>
		{#if purchasable}
			<button class="btn-primary" {disabled} on:click={() => dispatch('buy', item.id)}>
				Acquista
			</button>
		{/if}
	</div>
</div>
