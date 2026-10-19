<script lang="ts">
	import type { ReviewInventoryPilot } from '$lib/review-counts-types';
	import { Button } from '$lib/components/ui/button';

	let {
		pilot,
		disabled = false,
		onadjust
	}: {
		pilot: ReviewInventoryPilot;
		disabled?: boolean;
		onadjust: (name: string, delta: -1 | 1) => void;
	} = $props();
</script>

{#if pilot.cards.length === 0}
	<p class="text-sm text-muted-foreground">Nessuna carta sponsor per questo pilota.</p>
{:else}
	<ul class="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
		{#each pilot.cards as card (card.card_name)}
			<li class="min-w-0 rounded-lg border p-2">
				<img src="/media/{card.card_path}" alt={card.card_name} class="mx-auto w-24 rounded" />
				<p class="mt-2 text-center text-sm break-words">{card.card_name}</p>
				<p class="text-center text-lg font-semibold" aria-live="polite">
					{card.remaining}/{card.total}
				</p>
				<p class="mb-2 text-center text-xs text-muted-foreground">
					Partenza {card.start} · Bonus S {card.gifted}
				</p>
				<div class="flex justify-center gap-2">
					<Button
						type="button"
						size="sm"
						variant="outline"
						disabled={disabled || card.remaining === 0}
						onclick={() => onadjust(card.card_name, -1)}
						aria-label={`Togli una copia di ${card.card_name}`}
					>−</Button>
					<Button
						type="button"
						size="sm"
						variant="outline"
						disabled={disabled || card.remaining >= card.total}
						onclick={() => onadjust(card.card_name, 1)}
						aria-label={`Ripristina una copia di ${card.card_name}`}
					>+</Button>
				</div>
			</li>
		{/each}
	</ul>
{/if}
