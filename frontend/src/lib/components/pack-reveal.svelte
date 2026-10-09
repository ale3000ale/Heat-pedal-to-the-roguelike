<script lang="ts">
	import { untrack } from 'svelte';
	import { scale } from 'svelte/transition';
	import CardTile from '$lib/components/CardTile.svelte';
	import { Button } from '$lib/components/ui/button';
	import type { RevealedCard } from '$lib/shop-cards';

	// Carte nell'ordine di apertura (prima le modifiche, poi gli sponsor), tutte coperte.
	// Ogni tocco gira solo la carta toccata; `done` diventa vero quando sono tutte girate.
	// Il componente nasce ogni volta che la finestra si apre, quindi riparte da zero.
	let { cards, done = $bindable(false) }: { cards: RevealedCard[]; done?: boolean } = $props();

	let flipped = $state<boolean[]>(untrack(() => cards.map(() => false)));
	let remaining = $derived(flipped.filter((value) => !value).length);

	$effect(() => {
		done = remaining === 0;
	});

	function flip(index: number) {
		flipped[index] = true;
	}

	function flipAll() {
		flipped = flipped.map(() => true);
	}
</script>

<div class="space-y-4">
	{#if cards.length === 0}
		<p class="text-sm text-muted-foreground">Nessuna carta.</p>
	{/if}

	<div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
		{#each cards as item, index (index)}
			{#if flipped[index]}
				<div class="space-y-1" in:scale={{ duration: 300, start: 0.8 }}>
					<CardTile card={item.card} title="Copie ottenute" />
					<p class="text-xs text-muted-foreground">
						{item.section === 'modifiche' ? 'Modifica' : 'Sponsor'}
					</p>
				</div>
			{:else}
				<button
					type="button"
					onclick={() => flip(index)}
					aria-label={`Gira la carta ${index + 1}`}
					class="flex aspect-[2/3] w-full items-center justify-center rounded-lg border-2 border-dashed bg-muted text-2xl font-bold transition hover:ring-2 hover:ring-primary"
				>
					?
				</button>
			{/if}
		{/each}
	</div>

	{#if remaining > 0}
		<div class="flex flex-wrap items-center justify-between gap-3">
			<p class="text-sm text-muted-foreground">Carte da girare: {remaining}</p>
			<Button size="sm" variant="outline" onclick={flipAll}>Salta</Button>
		</div>
	{:else if cards.length > 0}
		<p class="text-sm text-muted-foreground">Hai girato tutte le carte.</p>
	{/if}
</div>
