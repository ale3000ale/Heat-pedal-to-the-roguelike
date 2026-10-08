<script lang="ts">
	import { onMount } from 'svelte';
	import { afterNavigate } from '$app/navigation';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { buyPack, fetchMyShops, fetchShop } from '$lib/shop-api';
	import { packImageUrl, revealOrder } from '$lib/shop-cards';
	import { shopSelection } from '$lib/shop-selection.svelte';
	import type { PurchaseResult, ShopPack, ShopPilotRef, ShopView } from '$lib/shop-types';
	import Modal from '$lib/components/modal.svelte';
	import PackReveal from '$lib/components/pack-reveal.svelte';
	import ShopInventoryModal from '$lib/components/shop-inventory-modal.svelte';
	import { Button } from '$lib/components/ui/button';

	type Area = 'modifiche' | 'sponsor';

	const selectClass =
		'h-8 rounded-md border border-input bg-background px-2 text-sm disabled:opacity-50';
	const championshipId = Number(page.params.id);

	let shop = $state<ShopView | null>(null);
	let pilots = $state<ShopPilotRef[]>([]);
	let selectedPilot = $state('');
	let area = $state<Area>('modifiche');
	let fromList = $state(false);
	let error = $state<string | null>(null);
	let buyError = $state<string | null>(null);
	let busy = $state(false);
	let result = $state<PurchaseResult | null>(null);
	let resultOpen = $state(false);
	let inventoryOpen = $state(false);

	// Area modifiche = pacchetti da pagare in oro; area sponsor = punti sponsor.
	let visiblePacks = $derived(
		shop?.packs.filter((p) => p.currency === (area === 'modifiche' ? 'gold' : 'sponsor')) ?? []
	);
	let revealed = $derived(result ? revealOrder(result) : []);

	// Il ritorno dipende da dove si arriva: dall'elenco dei negozi si torna all'elenco,
	// da ogni altra pagina (anche dopo un ricaricamento) al campionato.
	afterNavigate(({ from }) => {
		fromList = from?.route.id === '/shop';
	});

	function message(e: unknown): string {
		return e instanceof Error ? e.message : 'Errore sconosciuto';
	}

	function currencyLabel(currency: string): string {
		return currency === 'gold' ? 'oro' : 'punti sponsor';
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
			const chosen = pilots.find((p) => p.id === shopSelection.pilotId) ?? pilots[0];
			shopSelection.pilotId = null;
			if (chosen) selectedPilot = String(chosen.id);
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
							<span class="text-sm font-semibold">
								{pack.cost}
								{currencyLabel(pack.currency)}
							</span>
							{#if pack.sold_out}
								<span class="text-sm font-medium text-red-600">Terminato</span>
							{:else}
								<Button size="sm" onclick={() => buy(pack)} disabled={busy || !canBuy(view, pack)}>
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
	{#if fromList}
		<a href={resolve('/shop')} class="text-sm text-muted-foreground hover:text-foreground">
			← Negozio
		</a>
	{:else}
		<a
			href={resolve('/championships/[id]', { id: String(championshipId) })}
			class="text-sm text-muted-foreground hover:text-foreground"
		>
			← Campionato
		</a>
	{/if}

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
						{shop.pilot.name} · {shop.pilot.gold} oro · {shop.pilot.sponsor} punti sponsor
					</p>
				{/if}
			</div>
			<div class="flex items-center gap-2">
				{#if shop.pilot}
					<Button size="sm" variant="outline" onclick={() => (inventoryOpen = true)}>
						Inventario
					</Button>
				{/if}
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

		<div class="flex gap-2" role="group" aria-label="Area del negozio">
			<Button
				size="sm"
				variant={area === 'modifiche' ? 'default' : 'outline'}
				aria-pressed={area === 'modifiche'}
				onclick={() => (area = 'modifiche')}
			>
				Area modifiche
			</Button>
			<Button
				size="sm"
				variant={area === 'sponsor' ? 'default' : 'outline'}
				aria-pressed={area === 'sponsor'}
				onclick={() => (area = 'sponsor')}
			>
				Area sponsor
			</Button>
		</div>

		<section class="space-y-3">
			<h2 class="text-lg font-semibold">
				{area === 'modifiche' ? 'Pacchetti modifiche (oro)' : 'Pacchetti sponsor (punti sponsor)'}
			</h2>
			{@render packList(shop, visiblePacks)}
		</section>
	{/if}
</main>

<Modal bind:open={resultOpen} title={result ? result.pack_name : 'Pacchetto'}>
	<PackReveal cards={revealed} />
</Modal>

<ShopInventoryModal bind:open={inventoryOpen} {championshipId} pilotId={shop?.pilot?.id ?? null} />
