<script lang="ts">
	import { scale } from 'svelte/transition';
	import CardTile from '$lib/components/CardTile.svelte';
	import { Button } from '$lib/components/ui/button';
	import type { RevealedCard } from '$lib/shop-cards';

	// Carte nell'ordine di apertura (prima le modifiche, poi gli sponsor).
	// Il componente nasce ogni volta che la finestra si apre, quindi riparte da zero.
	let { cards }: { cards: RevealedCard[] } = $props();

	let revealedCount = $state(0);
	let visible = $derived(cards.slice(0, revealedCount));
	let remaining = $derived(cards.length - revealedCount);

	function revealNext() {
		if (revealedCount < cards.length) revealedCount += 1;
	}

	function revealAll() {
		revealedCount = cards.length;
	}
</script>

<div class="space-y-4">
	{#if cards.length === 0}
		<p class="text-sm text-muted-foreground">Nessuna carta.</p>
	{/if}

	{#if visible.length > 0}
		<div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
			{#each visible as item, index (index)}
				<div class="space-y-1" in:scale={{ duration: 300, start: 0.8 }}>
					<CardTile card={item.card} title="Copie ottenute" />
					<p class="text-xs text-muted-foreground">
						{item.section === 'modifiche' ? 'Modifica' : 'Sponsor'}
					</p>
				</div>
			{/each}
		</div>
	{/if}

	{#if remaining > 0}
		<div class="flex items-center gap-4">
			<button
				type="button"
				onclick={revealNext}
				aria-label="Gira la prossima carta"
				class="flex aspect-[2/3] w-24 items-center justify-center rounded-lg border-2 border-dashed bg-muted text-2xl font-bold transition hover:ring-2 hover:ring-primary"
			>
				?
			</button>
			<div class="flex flex-1 flex-col items-start gap-2">
				<p class="text-sm text-muted-foreground">
					Tocca la carta per girarla. Ne restano {remaining}.
				</p>
				<Button size="sm" variant="outline" onclick={revealAll}>Salta</Button>
			</div>
		</div>
	{/if}
</div>
