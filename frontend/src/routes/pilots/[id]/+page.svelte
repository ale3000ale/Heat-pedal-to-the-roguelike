<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { api } from '$lib/api';
	import type { PilotDetail } from '$lib/types';
	import CardTile from '$lib/components/CardTile.svelte';
	import * as Card from '$lib/components/ui/card';

	const MAX_GAME_DECK = 15;

	let pilot = $state<PilotDetail | null>(null);
	let error = $state<string | null>(null);
	let busy = $state(false);

	let total = (cards: { copies: number }[]) => cards.reduce((sum, c) => sum + c.copies, 0);

	let gameTotal = $derived(pilot ? total(pilot.game_deck) : 0);
	let full = $derived(gameTotal >= MAX_GAME_DECK);
	let locked = $derived(pilot?.championship != null);

	onMount(async () => {
		try {
			pilot = await api<PilotDetail>(`/pilots/${page.params.id}`);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		}
	});

	// Sposta una copia della carta: 'add' = inventario -> mazzo, 'remove' = mazzo -> inventario.
	async function move(path: string, action: 'add' | 'remove') {
		if (busy || !pilot) return;
		busy = true;
		error = null;
		try {
			pilot = await api<PilotDetail>(`/pilots/${pilot.id}/deck/${action}`, {
				method: 'POST',
				body: { path }
			});
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			busy = false;
		}
	}
</script>

<svelte:head><title>{pilot ? pilot.name : 'Pilota'} - Heat</title></svelte:head>

<main class="mx-auto max-w-5xl space-y-6 p-6">
	<a href={resolve('/team')} class="text-sm text-muted-foreground hover:text-foreground">
		← Team e piloti
	</a>

	{#if !pilot}
		{#if error}
			<p class="text-sm text-destructive" role="alert">{error}</p>
		{:else}
			<p class="text-muted-foreground">Caricamento…</p>
		{/if}
	{:else}
		<h1 class="text-2xl font-bold">{pilot.name}</h1>
		<p class="text-sm text-muted-foreground">
			Gold {pilot.gold} · Sponsor {pilot.sponsor} · Punti {pilot.point}
		</p>

		{#if pilot.championship}
			<p class="text-sm">
				Campionato attivo:
				<a
					href={resolve(`/championships/${pilot.championship.id}`)}
					class="font-semibold underline"
				>
					{pilot.championship.name}
				</a>
				· i mazzi non si possono modificare.
			</p>
		{/if}

		{#if error}
			<p class="text-sm text-destructive" role="alert">{error}</p>
		{/if}

		<Card.Root>
			<Card.Header>
				<Card.Title>Mazzo da gioco</Card.Title>
				<Card.Description>
					<span class={full ? 'font-semibold text-destructive' : ''}>
						{gameTotal}/{MAX_GAME_DECK} carte
					</span>
					{#if !locked}· clicca una carta per riportarla nell'inventario{/if}
				</Card.Description>
			</Card.Header>
			<Card.Content>
				{#if pilot.game_deck.length === 0}
					<p class="text-sm text-muted-foreground">Il mazzo da gioco è vuoto.</p>
				{:else}
					<div class="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-6">
						{#each pilot.game_deck as card (card.path)}
							<CardTile
								{card}
								disabled={locked || busy}
								title="Copie nel mazzo"
								onclick={() => move(card.path, 'remove')}
							/>
						{/each}
					</div>
				{/if}
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Header>
				<Card.Title>Inventario</Card.Title>
				<Card.Description>
					{total(pilot.inventory)} carte
					{#if !locked}· clicca una carta per metterla nel mazzo{/if}
				</Card.Description>
			</Card.Header>
			<Card.Content>
				{#if pilot.inventory.length === 0}
					<p class="text-sm text-muted-foreground">L'inventario è vuoto.</p>
				{:else}
					<div class="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-6">
						{#each pilot.inventory as card (card.path)}
							<CardTile
								{card}
								disabled={locked || busy || full}
								title="Copie in inventario"
								onclick={() => move(card.path, 'add')}
							/>
						{/each}
					</div>
				{/if}
			</Card.Content>
		</Card.Root>
	{/if}
</main>
