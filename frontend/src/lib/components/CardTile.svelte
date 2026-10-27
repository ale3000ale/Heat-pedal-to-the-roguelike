<script lang="ts">
	import type { CardEntry } from '$lib/types';
	import RacingIcon from '$lib/components/racing-icon.svelte';

	// Se `onclick` è passato la carta diventa un pulsante (usato per spostarla tra i mazzi).
	// Con `compact` la carta è più piccola: il nome sta sotto e le copie sopra l'immagine.
	// Con `hoverZoom` false il passaggio del mouse non ingrandisce né solleva la carta.
	// Con `hoverFocus` il passaggio del mouse mostra un contorno; `selected` lo mantiene.
	let {
		card,
		onclick,
		disabled = false,
		compact = false,
		hoverZoom = true,
		hoverFocus = false,
		selected = false,
		title = 'Copie possedute'
	}: {
		card: CardEntry;
		onclick?: () => void;
		disabled?: boolean;
		compact?: boolean;
		hoverZoom?: boolean;
		hoverFocus?: boolean;
		selected?: boolean;
		title?: string;
	} = $props();

	let imgError = $state(false);
</script>

{#snippet content()}
	{#if compact}
		<span class="relative block overflow-hidden rounded-t-lg bg-[#0e111a]">
			{#if !imgError}
				<img
					src="/media/{card.path}"
					alt={card.name}
					onerror={() => (imgError = true)}
					class={`aspect-[2/3] w-full object-cover transition-transform duration-300 ${hoverZoom ? 'group-hover:scale-105' : ''}`}
				/>
			{:else}
				<div
					class="flex aspect-[2/3] w-full flex-col items-center justify-center bg-[#151926] p-2 text-center"
				>
					<RacingIcon name="speedometer" size="md" class="mb-1 text-amber-400" />
					<span class="line-clamp-2 font-racing text-[10px] font-bold text-white uppercase"
						>{card.name}</span
					>
				</div>
			{/if}
			<span
				class="absolute top-1.5 right-1.5 rounded-full border border-white/20 bg-gradient-to-r from-red-600 to-amber-500 px-1.5 py-0.5 font-racing text-[10px] font-bold text-white shadow-md"
				{title}
			>
				×{card.copies}
			</span>
		</span>
		<span class="block truncate bg-[#121622] px-1.5 py-1 text-[11px] font-medium text-white/90"
			>{card.name}</span
		>
	{:else}
		<div class="relative overflow-hidden rounded-t-lg bg-[#0e111a]">
			{#if !imgError}
				<img
					src="/media/{card.path}"
					alt={card.name}
					onerror={() => (imgError = true)}
					class={`aspect-[2/3] w-full object-cover transition-transform duration-300 ${hoverZoom ? 'group-hover:scale-105' : ''}`}
				/>
			{:else}
				<div
					class="flex aspect-[2/3] w-full flex-col items-center justify-center bg-[#151926] p-4 text-center"
				>
					<RacingIcon name="speedometer" size="lg" class="mb-2 text-amber-400" />
					<span class="font-racing text-xs font-bold text-white uppercase">{card.name}</span>
				</div>
			{/if}
		</div>
		<span class="flex items-center justify-between gap-2 bg-[#121622] px-2.5 py-2 text-xs">
			<span class="truncate font-bold tracking-wide text-white">{card.name}</span>
			<span
				class="rounded-full border border-white/20 bg-gradient-to-r from-red-600 to-amber-500 px-2 py-0.5 font-racing text-xs font-black text-white shadow-md"
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
		class={`group block w-full overflow-hidden rounded-xl border border-white/10 bg-[#161a26] text-left transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-50 ${hoverZoom ? 'enabled:hover:-translate-y-1 enabled:hover:border-primary/60 enabled:hover:shadow-lg enabled:hover:shadow-primary/25' : ''} ${hoverFocus ? 'enabled:hover:ring-2 enabled:hover:ring-primary' : ''} ${selected ? 'ring-2 ring-primary' : ''}`}
	>
		{@render content()}
	</button>
{:else}
	<div
		class="group overflow-hidden rounded-xl border border-white/10 bg-[#161a26] transition-all duration-200 hover:border-white/20"
	>
		{@render content()}
	</div>
{/if}
