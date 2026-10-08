<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import { fetchMyShops } from '$lib/shop-api';
	import type { ShopEntry } from '$lib/shop-types';
	import * as Card from '$lib/components/ui/card';

	let shops = $state<ShopEntry[] | null>(null);
	let error = $state<string | null>(null);

	onMount(async () => {
		try {
			shops = (await fetchMyShops()).shops;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		}
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
		<ul class="grid gap-4 sm:grid-cols-2">
			{#each shops as shop (shop.championship_id)}
				<li>
					<a
						href={resolve('/championships/[id]/shop', { id: String(shop.championship_id) })}
						class="block hover:opacity-90"
					>
						<Card.Root>
							<Card.Header>
								<Card.Title>{shop.championship_name}</Card.Title>
								<Card.Description>
									Piloti iscritti: {shop.pilots.map((p) => p.name).join(', ')}
								</Card.Description>
							</Card.Header>
						</Card.Root>
					</a>
				</li>
			{/each}
		</ul>
	{/if}
</main>
