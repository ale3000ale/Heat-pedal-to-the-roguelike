<script lang="ts">
	import type { AdminDeckRead } from '$lib/admin-pilot-cards-types';
	import { countAdminDeckCopies } from '$lib/admin-pilot-cards-view';
	import CardTile from '$lib/components/CardTile.svelte';

	let {
		title,
		deck,
		gameDeck = false,
		onmove,
		disabled = false,
		destination
	}: {
		title: string;
		deck: AdminDeckRead;
		gameDeck?: boolean;
		onmove?: (path: string) => void;
		disabled?: boolean;
		destination?: string;
	} = $props();
	const copies = $derived(countAdminDeckCopies(deck));
</script>

<details class="rounded-lg border p-3">
	<summary class="cursor-pointer font-medium">
		{title}
		{#if deck.available}
			<span>({copies}{gameDeck ? '/15' : ''})</span>
		{:else}
			<span>— non disponibile</span>
		{/if}
	</summary>
	<div class="mt-3 space-y-2">
		{#if !deck.available}
			<p class="text-sm text-muted-foreground">Contenitore non presente nel campionato.</p>
		{:else if deck.cards.length === 0}
			<p class="text-sm text-muted-foreground">Nessuna carta in questo contenitore.</p>
		{:else}
			{#if destination}
				<p class="text-sm text-muted-foreground">
					Un clic sposta una copia verso {destination} nella bozza.
				</p>
			{/if}
			<div class="grid grid-cols-2 gap-2 sm:grid-cols-3">
				{#each deck.cards as card (card.name)}
					<CardTile
						{card}
						compact
						{disabled}
						onclick={onmove ? () => onmove?.(card.path) : undefined}
						title="Copie nel contenitore"
					/>
				{/each}
			</div>
		{/if}
	</div>
</details>
