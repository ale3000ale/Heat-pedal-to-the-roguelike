<script lang="ts">
	import type { CardEntry } from '$lib/types';

	// Se `onclick` è passato la carta diventa un pulsante (usato per spostarla tra i mazzi).
	// Con `compact` la carta è più piccola: il nome sta sotto e le copie sopra l'immagine.
	let {
		card,
		onclick,
		disabled = false,
		compact = false,
		title = 'Copie possedute'
	}: {
		card: CardEntry;
		onclick?: () => void;
		disabled?: boolean;
		compact?: boolean;
		title?: string;
	} = $props();
</script>

{#snippet content()}
	{#if compact}
		<span class="relative block">
			<img
				src="/media/{card.path}"
				alt={card.name}
				loading="lazy"
				class="aspect-[2/3] w-full object-cover"
			/>
			<span
				class="absolute top-1 right-1 rounded-full bg-primary px-1.5 text-[10px] font-semibold text-primary-foreground"
				{title}
			>
				×{card.copies}
			</span>
		</span>
		<span class="block truncate px-1 py-0.5 text-[10px] font-medium">{card.name}</span>
	{:else}
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
	{/if}
{/snippet}

{#if onclick}
	<button
		type="button"
		{onclick}
		{disabled}
		class="block w-full overflow-hidden rounded-lg border bg-card text-left transition enabled:hover:ring-2 enabled:hover:ring-primary disabled:cursor-not-allowed disabled:opacity-50"
	>
		{@render content()}
	</button>
{:else}
	<div class="overflow-hidden rounded-lg border bg-card">
		{@render content()}
	</div>
{/if}
