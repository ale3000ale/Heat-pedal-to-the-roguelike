<script lang="ts">
	import CardTile from '$lib/components/cards/CardTile.svelte';
	import { Button } from '$lib/components/ui/button';
	import type { DraftCardSlot } from '$lib/draft/draft-types';

	// Senza onzoom la carta e di sola visione: nessun pulsante, aggiornata dallo snapshot.
	let {
		slot,
		enlarged = false,
		previewPilotName = null,
		pickedBy = null,
		chooseAllowed = false,
		disabled = false,
		onzoom,
		onchoose
	}: {
		slot: DraftCardSlot;
		enlarged?: boolean;
		previewPilotName?: string | null;
		pickedBy?: string | null;
		chooseAllowed?: boolean;
		disabled?: boolean;
		onzoom?: () => void;
		onchoose?: () => void;
	} = $props();
</script>

<div
	data-slot-id={slot.slot_id}
	class={enlarged
		? 'relative col-span-full mx-auto w-44 max-w-full sm:mx-0 sm:w-52 lg:w-60'
		: 'relative w-full min-w-0 sm:w-36'}
>
	<div class="relative space-y-2">
		<div class={previewPilotName ? 'rounded-xl ring-2 ring-yellow-300/80' : undefined}>
			<CardTile
				card={{ name: slot.name, path: slot.path, copies: 1 }}
				onclick={onzoom}
				{disabled}
				compact={!enlarged}
				hoverZoom={false}
				hoverFocus
				selected={enlarged}
				title="Singola copia nella draft"
			/>
		</div>
		{#if previewPilotName}
			<p
				class="flex w-fit max-w-full items-baseline rounded-full bg-yellow-300/80 px-2 py-0.5 text-xs font-semibold text-black sm:text-sm"
			>
				<span class="truncate">{previewPilotName} sta scegliendo</span><span
					aria-hidden="true"
					class="wave-dots"><span>.</span><span>.</span><span>.</span></span
				>
			</p>
		{/if}
		{#if pickedBy}
			<p class="text-sm">Scelta da {pickedBy}</p>
		{/if}
		{#if enlarged && chooseAllowed && slot.chosen_by === null && onchoose}
			<Button type="button" class="w-full" {disabled} onclick={() => onchoose?.()}>Scegli</Button>
		{/if}
	</div>
</div>

<style>
	.wave-dots {
		display: inline-flex;
		flex-shrink: 0;
	}
	.wave-dots span {
		display: inline-block;
		animation: draft-wave 1.2s ease-in-out infinite;
	}
	.wave-dots span:nth-child(2) {
		animation-delay: 0.15s;
	}
	.wave-dots span:nth-child(3) {
		animation-delay: 0.3s;
	}
	@keyframes draft-wave {
		0%,
		60%,
		100% {
			transform: translateY(0);
		}
		30% {
			transform: translateY(-0.3em);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.wave-dots span {
			animation: none;
		}
	}
</style>
