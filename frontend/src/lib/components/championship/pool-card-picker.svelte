<script lang="ts">
	import { isUploadedCard } from '$lib/cards/card-origin';
	import type { CardEntry, PoolKind } from '$lib/types';
	import { Button } from '$lib/components/ui/button';

	// Elenco delle carte di una pool di base con le copie da tenere. Le carte caricate a mano
	// hanno il nome arancione e il tasto «Elimina»; quelle di base non si possono eliminare.
	interface Props {
		cards: CardEntry[];
		kind: PoolKind;
		picks: Record<string, number>;
		busy: string | null;
		onpick: (card: CardEntry, value: number) => void;
		ondelete: (card: CardEntry) => void;
	}

	let { cards, kind, picks, busy, onpick, ondelete }: Props = $props();
</script>

<ul class="divide-y">
	{#each cards as card (card.path)}
		{@const uploaded = isUploadedCard(card, kind)}
		<li class="flex items-center gap-3 py-2">
			<span class="flex-1" class:uploaded>{card.name}</span>
			{#if uploaded}
				<span class="text-xs text-muted-foreground">caricata a mano</span>
			{/if}
			<span class="text-sm text-muted-foreground">max {card.copies}</span>
			<input
				type="number"
				class="h-9 w-20 rounded-md border bg-background px-2 text-sm"
				min={0}
				max={card.copies}
				aria-label={`Copie di ${card.name}`}
				value={picks[card.name] ?? 0}
				oninput={(e) => onpick(card, e.currentTarget.valueAsNumber)}
			/>
			{#if uploaded}
				<Button
					type="button"
					size="sm"
					variant="outline"
					disabled={busy === `card-${card.name}`}
					onclick={() => ondelete(card)}
				>
					Elimina
				</Button>
			{/if}
		</li>
	{/each}
</ul>

<style>
	.uploaded {
		color: oklch(0.646 0.222 41.116);
		font-weight: 500;
	}

	:global(.dark) .uploaded {
		color: oklch(0.75 0.183 55.934);
	}
</style>
