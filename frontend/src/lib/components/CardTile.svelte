<script lang="ts">
	import type { CardEntry } from '$lib/types';

	// Se `onclick` è passato la carta diventa un pulsante (usato per spostarla tra i mazzi).
	let {
		card,
		onclick,
		disabled = false,
		title = 'Copie possedute'
	}: {
		card: CardEntry;
		onclick?: () => void;
		disabled?: boolean;
		title?: string;
	} = $props();
</script>

{#snippet content()}
	<img
		src="/media/{card.path}"
		alt={card.name}
		loading="lazy"
		class="aspect-[2/3] w-full object-cover"
	/>
	<span class="flex items-center justify-between gap-2 px-2 py-1.5 text-sm">
		<span class="truncate font-medium">{card.name}</span>
		<span
			class="rounded-full bg-primary px-2 py-0.5 text-xs font-semibold text-primary-foreground"
			{title}
		>
			×{card.copies}
		</span>
	</span>
{/snippet}

{#if onclick}
	<button
		type="button"
		{onclick}
		{disabled}
		class="block overflow-hidden rounded-lg border bg-card text-left transition enabled:hover:ring-2 enabled:hover:ring-primary disabled:cursor-not-allowed disabled:opacity-50"
	>
		{@render content()}
	</button>
{:else}
	<div class="overflow-hidden rounded-lg border bg-card">
		{@render content()}
	</div>
{/if}
