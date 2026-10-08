<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import { fetchMyShops, fetchShop } from '$lib/shop-api';
	import { shopSelection } from '$lib/shop-selection.svelte';
	import type { ShopEntry, ShopPilot } from '$lib/shop-types';
	import * as Card from '$lib/components/ui/card';

	let shops = $state<ShopEntry[] | null>(null);
	let balances = $state<Record<number, ShopPilot>>({});
	let error = $state<string | null>(null);

	// Legge il saldo di un pilota dal negozio del suo campionato.
	async function loadBalance(championshipId: number, pilotId: number) {
		try {
			const view = await fetchShop(championshipId, pilotId);
			if (view.pilot) balances[pilotId] = view.pilot;
		} catch {
			// Il pilota resta senza saldo: l'errore vero lo mostra il negozio.
		}
	}

	onMount(async () => {
		let list: ShopEntry[];
		try {
			list = (await fetchMyShops()).shops;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
			return;
		}
		shops = list;
		await Promise.all(
			list.flatMap((shop) =>
				shop.pilots.map((pilot) => loadBalance(shop.championship_id, pilot.id))
			)
		);
	});
</script>

<svelte:head><title>Negozio - Heat</title></svelte:head>

<main class="mx-auto max-w-5xl space-y-6 p-6">
	<h1 class="text-2xl font-bold">Negozio</h1>

	{#if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{:else if shops === null}
		<p class="text-muted-foreground">Caricamento…</p>
	{:else if shops.length === 0}
		<p class="text-sm text-muted-foreground">
			Non partecipi a nessun campionato attivo con un tuo pilota.
		</p>
	{:else}
		<div class="grid gap-4 sm:grid-cols-2">
			{#each shops as shop (shop.championship_id)}
				<Card.Root>
					<Card.Header>
						<Card.Title>{shop.championship_name}</Card.Title>
						<Card.Description>Scegli il pilota con cui entrare nel negozio.</Card.Description>
					</Card.Header>
					<Card.Content>
						<ul class="divide-y">
							{#each shop.pilots as pilot (pilot.id)}
								{@const balance = balances[pilot.id]}
								<li>
									<a
										href={resolve('/championships/[id]/shop', {
											id: String(shop.championship_id)
										})}
										onclick={() => (shopSelection.pilotId = pilot.id)}
										class="flex items-center gap-3 py-2 hover:bg-accent"
									>
										<span class="flex-1 font-medium">{pilot.name}</span>
										<span class="text-sm text-muted-foreground">
											{#if balance}
												{balance.gold} oro · {balance.sponsor} punti sponsor
											{:else}
												…
											{/if}
										</span>
									</a>
								</li>
							{/each}
						</ul>
					</Card.Content>
				</Card.Root>
			{/each}
		</div>
	{/if}
</main>
