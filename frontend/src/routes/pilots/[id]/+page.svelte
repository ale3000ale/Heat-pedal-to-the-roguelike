<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { api } from '$lib/api';
	import type { PilotDetail } from '$lib/types';
	import CardTile from '$lib/components/CardTile.svelte';
	import * as Card from '$lib/components/ui/card';

	let pilot = $state<PilotDetail | null>(null);
	let error = $state<string | null>(null);

	let total = (cards: { copies: number }[]) => cards.reduce((sum, c) => sum + c.copies, 0);

	onMount(async () => {
		try {
			pilot = await api<PilotDetail>(`/pilots/${page.params.id}`);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		}
	});
</script>

<svelte:head><title>{pilot ? pilot.name : 'Pilota'} - Heat</title></svelte:head>

<main class="mx-auto max-w-5xl space-y-6 p-6">
	<a href={resolve('/team')} class="text-sm text-muted-foreground hover:text-foreground">
		← Team e piloti
	</a>

	{#if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{:else if !pilot}
		<p class="text-muted-foreground">Caricamento…</p>
	{:else}
		<h1 class="text-2xl font-bold">{pilot.name}</h1>
		<p class="text-sm text-muted-foreground">
			Gold {pilot.gold} · Sponsor {pilot.sponsor} · Punti {pilot.point}
		</p>

		<Card.Root>
			<Card.Header>
				<Card.Title>Mazzo da gioco</Card.Title>
				<Card.Description>{total(pilot.game_deck)} carte</Card.Description>
			</Card.Header>
			<Card.Content>
				{#if pilot.game_deck.length === 0}
					<p class="text-sm text-muted-foreground">Il mazzo da gioco è vuoto.</p>
				{:else}
					<div class="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-6">
						{#each pilot.game_deck as card (card.path)}
							<CardTile {card} />
						{/each}
					</div>
				{/if}
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Header>
				<Card.Title>Inventario</Card.Title>
				<Card.Description>{total(pilot.inventory)} carte</Card.Description>
			</Card.Header>
			<Card.Content>
				{#if pilot.inventory.length === 0}
					<p class="text-sm text-muted-foreground">L'inventario è vuoto.</p>
				{:else}
					<div class="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-6">
						{#each pilot.inventory as card (card.path)}
							<CardTile {card} />
						{/each}
					</div>
				{/if}
			</Card.Content>
		</Card.Root>
	{/if}
</main>
