<!-- frontend/src/routes/negozio/[id]/+page.svelte -->
<!-- Negozio di un campionato specifico: recap wallet del pilota scelto + acquisto oggetti. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { authStore } from '$lib/store/auth';
	import { apiRequest } from '$lib/api';
	import ShopItemCard from '$lib/components/ShopItemCard.svelte';

	interface ShopItemOut {
		id: number; name: string; description?: string | null;
		price_gold: number; price_points: number; requirements?: string | null;
	}
	interface PilotOut { id: number; name: string; gold: number; point: number }
	interface WalletOut { pilot_id: number; pilot_name: string; gold: number; points: number }

	const championshipId = $page.params.id;

	let items: ShopItemOut[] = [];
	let myPilots: PilotOut[] = [];
	let selectedPilotId: number | null = null;
	let wallet: WalletOut | null = null;
	let loading = true;
	let errorMsg = '';
	let buyMsg = '';

	// loadShop()
	// Nessun parametro.
	// Carica gli oggetti del negozio per il campionato corrente e i piloti dell'utente per scegliere
	// con quale pilota effettuare gli acquisti.
	async function loadShop(): Promise<void> {
		loading = true;
		errorMsg = '';
		try {
			items = await apiRequest<ShopItemOut[]>(`/shop/championship/${championshipId}`, { auth: true });
			myPilots = await apiRequest<PilotOut[]>('/pilots', { auth: true });
			if (myPilots.length > 0) {
				selectedPilotId = myPilots[0].id;
				await loadWallet();
			}
		} catch (e) {
			errorMsg = e instanceof Error ? e.message : 'Errore nel caricamento del negozio';
		} finally {
			loading = false;
		}
	}

	// loadWallet()
	// Nessun parametro (usa selectedPilotId corrente).
	// Recupera gold e punti disponibili del pilota selezionato per questo campionato.
	async function loadWallet(): Promise<void> {
		if (!selectedPilotId) return;
		wallet = await apiRequest<WalletOut>(`/shop/wallet/${selectedPilotId}?championship_id=${championshipId}`, { auth: true });
	}

	// handleBuy(event)
	// event.detail: id dell'oggetto da acquistare.
	// Invia la richiesta di acquisto al backend, che scala gold/point del pilota selezionato.
	// Passaggio critico: aggiorna il wallet locale solo dopo la conferma del backend, per restare coerente coi fondi reali.
	async function handleBuy(event: CustomEvent<number>): Promise<void> {
		buyMsg = '';
		if (!selectedPilotId) return;
		try {
			await apiRequest('/shop/purchase', {
				method: 'POST', auth: true,
				body: { pilot_id: selectedPilotId, championship_id: Number(championshipId), item_id: event.detail }
			});
			buyMsg = 'Acquisto completato!';
			await loadWallet();
		} catch (e) {
			buyMsg = e instanceof Error ? e.message : 'Errore durante l\'acquisto';
		}
	}

	onMount(loadShop);
</script>

<svelte:head><title>Heat - Negozio campionato</title></svelte:head>

<h1 class="font-display text-2xl font-bold mb-6">Negozio campionato</h1>

{#if loading}
	<p>Caricamento…</p>
{:else if errorMsg}
	<p class="text-racing-red">{errorMsg}</p>
{:else}
	{#if myPilots.length > 1}
		<label class="block mb-4">
			<span class="text-sm font-medium">Pilota</span>
			<select class="input-field" bind:value={selectedPilotId} on:change={loadWallet}>
				{#each myPilots as p}<option value={p.id}>{p.name}</option>{/each}
			</select>
		</label>
	{/if}

	{#if wallet}
		<div class="app-card mb-6 max-w-sm">
			<p class="font-semibold">{wallet.pilot_name}</p>
			<p class="text-sm opacity-70">Gold: {wallet.gold} · Punti: {wallet.points}</p>
		</div>
	{/if}

	{#if buyMsg}<p class="mb-4 text-sm">{buyMsg}</p>{/if}

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		{#each items as item}
			<ShopItemCard
				{item}
				purchasable={true}
				disabled={!wallet || wallet.gold < item.price_gold || wallet.points < item.price_points}
				on:buy={handleBuy}
			/>
		{/each}
		{#if items.length === 0}<p class="text-sm opacity-70">Nessun oggetto disponibile per questo campionato.</p>{/if}
	</div>
{/if}
