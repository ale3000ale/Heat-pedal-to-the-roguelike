<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { buyPack, fetchMyShops, fetchShop } from '$lib/shop-api';
	import { packImageUrl, revealOrder } from '$lib/shop-cards';
	import type { PurchaseResult, ShopPack, ShopPilotRef, ShopView } from '$lib/shop-types';
	import CardTile from '$lib/components/CardTile.svelte';
	import Modal from '$lib/components/modal.svelte';
	import { Button } from '$lib/components/ui/button';

	const selectClass =
		'h-8 rounded-md border border-input bg-background px-2 text-sm disabled:opacity-50';
	const championshipId = Number(page.params.id);

	let shop = $state<ShopView | null>(null);
	let pilots = $state<ShopPilotRef[]>([]);
	let selectedPilot = $state('');
	let error = $state<string | null>(null);
	let buyError = $state<string | null>(null);
	let busy = $state(false);
	let result = $state<PurchaseResult | null>(null);
	let resultOpen = $state(false);

	let goldPacks = $derived(shop?.packs.filter((p) => p.currency === 'gold') ?? []);
	let sponsorPacks = $derived(shop?.packs.filter((p) => p.currency === 'sponsor') ?? []);
	let revealed = $derived(result ? revealOrder(result) : []);

	function message(e: unknown): string {
		return e instanceof Error ? e.message : 'Errore sconosciuto';
	}

	// Saldo del pilota nella valuta del pacchetto.
	function balance(view: ShopView, pack: ShopPack): number {
		return pack.currency === 'gold' ? (view.pilot?.gold ?? 0) : (view.pilot?.sponsor ?? 0);
	}

	// Il pulsante resta spento se il negozio non è utilizzabile; il backend ha l'ultima parola.
	function canBuy(view: ShopView, pack: ShopPack): boolean {
		if (!view.pilot || view.read_only || view.locked || pack.sold_out) return false;
		return balance(view, pack) >= pack.cost;
	}

	async function loadShop() {
		error = null;
		try {
			const pilotId = selectedPilot === '' ? undefined : Number(selectedPilot);
			shop = await fetchShop(championshipId, pilotId);
		} catch (e) {
			shop = null;
			error = message(e);
		}
	}

	async function changePilot() {
		buyError = null;
		await loadShop();
	}

	async function buy(pack: ShopPack) {
		if (!shop?.pilot) return;
		buyError = null;
		busy = true;
		try {
			result = await buyPack(championshipId, shop.pilot.id, pack.id);
			resultOpen = true;
			await loadShop();
		} catch (e) {
			buyError = message(e);
		} finally {
			busy = false;
		}
	}

	onMount(async () => {
		try {
			const mine = await fetchMyShops();
			const entry = mine.shops.find((s) => s.championship_id === championshipId);
			pilots = entry?.pilots ?? [];
			if (pilots.length > 0) selectedPilot = String(pilots[0].id);
		} catch (e) {
			error = message(e);
			return;
		}
		await loadShop();
	});
</script>

{#snippet packList(view: ShopView, packs: ShopPack[])}
	{#if packs.length === 0}
		<p class="text-sm text-muted-foreground">Nessun pacchetto.</p>
	{:else}
		<ul class="grid gap-3 sm:grid-cols-2">
			{#each packs as pack (pack.id)}
				<li class="flex gap-3 rounded-lg border bg-card p-3">
					<img
						src={packImageUrl(pack.image_path)}
						alt={pack.name}
						loading="lazy"
						class="h-24 w-20 rounded object-cover"
					/>
					<div class="flex flex-1 flex-col gap-1">
						<span class="font-medium">{pack.name}</span>
						<span class="text-sm text-muted-foreground">
							{pack.modifiche_count} modifiche · {pack.sponsor_count} sponsor
						</span>
						{#if pack.filter_enabled && pack.filter_text}
							<span class="text-xs text-muted-foreground">Filtro: {pack.filter_text}</span>
						{/if}
						<div class="mt-auto flex items-center justify-between gap-2">
							<span class="text-sm font-semibold">{pack.cost} {pack.currency}</span>
							{#if pack.sold_out}
								<span class="text-sm font-medium text-red-600">Terminato</span>
							{:else}
								<Button
									size="sm"
									onclick={() => buy(pack)}
									disabled={busy || !canBuy(view, pack)}
								>
									Acquista
								</Button>
							{/if}
						</div>
					</div>
				</li>
			{/each}
		</ul>
	{/if}
{/snippet}

<svelte:head><title>{shop ? shop.championship_name : 'Negozio'} - Heat</title></svelte:head>

<main class="mx-auto max-w-5xl space-y-6 p-6">
	<a href={resolve('/shop')} class="text-sm text-muted-foreground hover:text-foreground">
		← Negozio
	</a>

	{#if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{:else if !shop}
		<p class="text-muted-foreground">Caricamento…</p>
	{:else}
		<div class="flex flex-wrap items-start justify-between gap-3">
			<div>
				<h1 class="text-2xl font-bold">{shop.championship_name}</h1>
				{#if shop.pilot}
					<p class="text-sm text-muted-foreground">
						{shop.pilot.name} · {shop.pilot.gold} gold · {shop.pilot.sponsor} sponsor
					</p>
				{/if}
			</div>
			{#if pilots.length > 1}
				<select
					class={selectClass}
					bind:value={selectedPilot}
					onchange={changePilot}
					aria-label="Pilota"
				>
					{#each pilots as p (p.id)}
						<option value={String(p.id)}>{p.name}</option>
					{/each}
				</select>
			{/if}
		</div>

		{#if shop.read_only}
			<p class="rounded-md border bg-muted px-3 py-2 text-sm">Negozio in sola lettura.</p>
		{:else if shop.locked}
			<p class="rounded-md border bg-muted px-3 py-2 text-sm">
				Negozio bloccato: c'è una gara in corso.
			</p>
		{/if}

		{#if buyError}
			<p class="text-sm text-destructive" role="alert">{buyError}</p>
		{/if}

		<section class="space-y-3">
			<h2 class="text-lg font-semibold">Pacchetti gold</h2>
			{@render packList(shop, goldPacks)}
		</section>

		<section class="space-y-3">
			<h2 class="text-lg font-semibold">Pacchetti sponsor</h2>
			{@render packList(shop, sponsorPacks)}
		</section>
	{/if}
</main>

<Modal bind:open={resultOpen} title={result ? result.pack_name : 'Pacchetto'}>
	<div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
		{#each revealed as item, index (index)}
			<div class="space-y-1">
				<CardTile card={item.card} title="Copie ottenute" />
				<p class="text-xs text-muted-foreground">
					{item.section === 'modifiche' ? 'Modifica' : 'Sponsor'}
				</p>
			</div>
		{/each}
	</div>
</Modal>
