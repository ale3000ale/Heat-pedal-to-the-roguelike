<script lang="ts">
	import CardTile from '$lib/components/CardTile.svelte';
	import { Button } from '$lib/components/ui/button';
	import type { DraftCardSlot } from '$lib/draft-types';

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
		onzoom: () => void;
		onchoose?: () => void;
	} = $props();
</script>

<div
	data-slot-id={slot.slot_id}
	class={enlarged ? 'relative w-56 sm:w-72' : 'relative w-28 sm:w-36'}
>
	{#if previewPilotName}
		<div
			aria-hidden="true"
			class="pointer-events-none absolute inset-x-2 -bottom-1 h-8 rounded-full bg-yellow-300/80 blur-md"
		></div>
	{/if}
	<div class="relative space-y-2">
		<CardTile
			card={{ name: slot.name, path: slot.path, copies: 1 }}
			onclick={onzoom}
			{disabled}
			compact={!enlarged}
			title="Singola copia nella draft"
		/>
		{#if previewPilotName}
			<p class="text-sm font-semibold text-yellow-300">Anteprima di {previewPilotName}</p>
		{/if}
		{#if pickedBy}
			<p class="text-sm">Scelta da {pickedBy}</p>
		{/if}
		{#if enlarged && chooseAllowed && slot.chosen_by === null && onchoose}
			<Button type="button" class="w-full" {disabled} onclick={() => onchoose?.()}>Scegli</Button>
		{/if}
	</div>
</div>
