<script lang="ts">
	import CardTile from '$lib/components/CardTile.svelte';
	import Modal from '$lib/components/modal.svelte';
	import { fetchInventory } from '$lib/shop-api';
	import type { ShopInventory } from '$lib/shop-types';

	// Riepilogo delle carte di un pilota: si carica ogni volta che la finestra si apre.
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
		<div class="space-y-4">
			<section class="space-y-2">
				<h3 class="font-semibold">Modifiche</h3>
				{#if inventory.modifiche.length === 0}
					<p class="text-sm text-muted-foreground">Nessuna carta.</p>
				{:else}
					<div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
						{#each inventory.modifiche as card (card.path)}
							<CardTile {card} />
						{/each}
					</div>
				{/if}
			</section>
			<section class="space-y-2">
				<h3 class="font-semibold">Sponsor</h3>
				{#if inventory.sponsor.length === 0}
					<p class="text-sm text-muted-foreground">Nessuna carta.</p>
				{:else}
					<div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
						{#each inventory.sponsor as card (card.path)}
							<CardTile {card} />
						{/each}
					</div>
				{/if}
			</section>
		</div>
	{/if}
</Modal>
