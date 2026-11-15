<script lang="ts">
	import CardTile from '$lib/components/cards/CardTile.svelte';
	import InventorySection from '$lib/components/shop/inventory-section.svelte';
	import Modal from '$lib/components/shared/modal.svelte';
	import { totalCopies } from '$lib/shop/inventory-count';
	import { fetchInventory } from '$lib/shop/shop-api';
	import type { ShopInventory } from '$lib/shop/shop-types';

	// Riepilogo delle carte di un pilota: si carica ogni volta che la finestra si apre.
	// Le sezioni Modifiche e Sponsor sono a scomparsa e partono chiuse.
	let {
		open = $bindable(false),
		championshipId,
		pilotId
	}: { open?: boolean; championshipId: number; pilotId: number | null } = $props();

	let inventory = $state<ShopInventory | null>(null);
	let error = $state<string | null>(null);

	async function load(id: number) {
		inventory = null;
		error = null;
		try {
			inventory = await fetchInventory(championshipId, id);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		}
	}

	$effect(() => {
		if (open && pilotId !== null) void load(pilotId);
	});
</script>

<Modal bind:open title={inventory ? `Inventario di ${inventory.pilot_name}` : 'Inventario'}>
	{#if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{:else if !inventory}
		<p class="text-muted-foreground">Caricamento…</p>
	{:else}
		<div class="space-y-3">
			<InventorySection title="Modifiche" count={totalCopies(inventory.modifiche)}>
				{#if inventory.modifiche.length === 0}
					<p class="text-sm text-muted-foreground">Nessuna carta.</p>
				{:else}
					<div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
						{#each inventory.modifiche as card (card.path)}
							<CardTile {card} />
						{/each}
					</div>
				{/if}
			</InventorySection>
			<InventorySection title="Sponsor" count={totalCopies(inventory.sponsor)}>
				{#if inventory.sponsor.length === 0}
					<p class="text-sm text-muted-foreground">Nessuna carta.</p>
				{:else}
					<div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
						{#each inventory.sponsor as card (card.path)}
							<CardTile {card} />
						{/each}
					</div>
				{/if}
			</InventorySection>
		</div>
	{/if}
</Modal>
