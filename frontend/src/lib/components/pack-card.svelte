<script lang="ts">
	import { packSummary } from '$lib/shop-admin-format';
	import { packImageUrl } from '$lib/shop-cards';
	import type { PackFields } from '$lib/shop-admin-types';
	import { Button } from '$lib/components/ui/button';

	// Scheda di un pacchetto con Modifica ed Elimina; l'eliminazione chiede conferma sul posto.
	// `locked` nasconde i pulsanti (campionato chiuso).
	let {
		pack,
		locked,
		onedit,
		ondelete
	}: {
		pack: PackFields;
		locked: boolean;
		onedit: () => void;
		ondelete: () => void | Promise<void>;
	} = $props();

	let confirming = $state(false);

	function ask() {
		confirming = true;
	}

	function cancel() {
		confirming = false;
	}
</script>

<li class="flex gap-3 rounded-lg border bg-card p-3">
	<img
		src={packImageUrl(pack.image_path)}
		alt={pack.name}
		loading="lazy"
		class="h-24 w-16 rounded object-cover"
	/>
	<div class="flex flex-1 flex-col gap-1">
		<span class="font-medium">{pack.name}</span>
		<span class="text-sm text-muted-foreground">{packSummary(pack)}</span>
		{#if pack.filter_enabled && pack.filter_text}
			<span class="text-xs text-muted-foreground">Filtro: {pack.filter_text}</span>
		{/if}
		{#if !locked}
			<div class="mt-auto flex flex-wrap items-center gap-2">
				{#if confirming}
					<span class="text-sm">Eliminare?</span>
					<Button size="sm" variant="destructive" onclick={ondelete}>Sì</Button>
					<Button size="sm" variant="outline" onclick={cancel}>No</Button>
				{:else}
					<Button size="sm" variant="outline" onclick={onedit}>Modifica</Button>
					<Button size="sm" variant="outline" onclick={ask}>Elimina</Button>
				{/if}
			</div>
		{/if}
	</div>
</li>
