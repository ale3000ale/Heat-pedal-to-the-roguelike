<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { api } from '$lib/api';
	import type { PilotDetail } from '$lib/types';
	import CardTile from '$lib/components/CardTile.svelte';
	import InventorySection from '$lib/components/inventory-section.svelte';
	import * as Card from '$lib/components/ui/card';
	import RacingIcon from '$lib/components/racing-icon.svelte';

	const MAX_GAME_DECK = 15;

	let pilot = $state<PilotDetail | null>(null);
	let error = $state<string | null>(null);
	let busy = $state(false);

	let total = (cards: { copies: number }[]) => cards.reduce((sum, c) => sum + c.copies, 0);

	let gameTotal = $derived(pilot ? total(pilot.game_deck) : 0);
	let full = $derived(gameTotal >= MAX_GAME_DECK);
	// Mazzo bloccato: una gara del campionato non ha ancora la revisione confermata.
	let locked = $derived(pilot?.deck_locked === true);

	onMount(async () => {
		try {
			pilot = await api<PilotDetail>(`/pilots/${page.params.id}`);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		}
	});

	// Torna alla pagina da cui si è arrivati (il campionato, l'elenco dei piloti...).
	// Se la pagina è stata aperta direttamente, senza una pagina precedente, va a Team e piloti.
	function goBack() {
		if (history.length > 1) history.back();
		else void goto(resolve('/team'));
	}

	// Ricarica il dettaglio: serve se il backend rifiuta lo spostamento perché la gara è partita.
	async function reload() {
		try {
			pilot = await api<PilotDetail>(`/pilots/${page.params.id}`);
		} catch {
			// Il messaggio d'errore dello spostamento resta visibile.
		}
	}

	// Sposta una copia della carta: 'add' = inventario -> mazzo, 'remove' = mazzo -> inventario.
	async function move(path: string, action: 'add' | 'remove') {
		if (busy || locked || !pilot) return;
		busy = true;
		error = null;
		try {
			pilot = await api<PilotDetail>(`/pilots/${pilot.id}/deck/${action}`, {
				method: 'POST',
				body: { path }
			});
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
			await reload();
		} finally {
			busy = false;
		}
	}
</script>

<svelte:head><title>{pilot ? pilot.name : 'Pilota'} - Heat</title></svelte:head>

<main class="mx-auto max-w-6xl space-y-6 px-4 py-8 sm:px-6">
	<button
		type="button"
		class="inline-flex items-center gap-1.5 text-xs font-racing uppercase tracking-wider text-muted-foreground hover:text-white transition-colors"
		onclick={goBack}
	>
		<span>←</span>
		<span>Torna al Garage / Paddock</span>
	</button>

	{#if !pilot}
		{#if error}
			<div class="rounded-xl border border-destructive/40 bg-destructive/15 p-3 text-xs text-red-300 flex items-center gap-2" role="alert">
				<RacingIcon name="flame" size="xs" />
				<span>{error}</span>
			</div>
		{:else}
			<div class="flex items-center justify-center p-12 text-muted-foreground">
				<RacingIcon name="speedometer" size="lg" class="animate-spin mr-3 text-primary" />
				<span class="font-racing text-lg uppercase tracking-wider">Caricamento scheda pilota e mazzi…</span>
			</div>
		{/if}
	{:else}
		<!-- Pilot Header Banner -->
		<div class="overflow-hidden rounded-2xl border border-white/10 bg-[#121622] shadow-xl">
			<div class="curb-bar" role="presentation"></div>
			<div class="p-6 flex flex-col md:flex-row md:items-center justify-between gap-6">
				<div class="flex items-center gap-4">
					<div class="racing-roundel h-12 w-12 text-lg font-black shrink-0 shadow-lg">
						#{pilot.id}
					</div>
					<div>
						<div class="flex items-center gap-2 mb-1">
							<span class="font-racing text-xs uppercase tracking-wider text-muted-foreground font-bold">
								Scheda Tecnica Pilota
							</span>
							{#if pilot.championship}
								<span class="text-xs text-muted-foreground">·</span>
								<a
									href={resolve(`/championships/${pilot.championship.id}`)}
									class="inline-flex items-center gap-1 text-xs font-bold text-amber-400 hover:text-amber-300"
								>
									<RacingIcon name="trophy" size="xs" />
									{pilot.championship.name}
								</a>
							{/if}
						</div>

						<h1 class="font-racing text-3xl sm:text-4xl font-black uppercase italic tracking-wide text-white">
							{pilot.name}
						</h1>

						<!-- Telemetry Badges -->
						<div class="mt-2.5 flex flex-wrap items-center gap-2.5">
							<span class="inline-flex items-center gap-1.5 rounded-full bg-amber-500/10 px-3 py-1 text-xs font-bold text-amber-400 border border-amber-500/20">
								<RacingIcon name="trophy" size="xs" />
								{pilot.gold} Gold Accumulato
							</span>
							<span class="inline-flex items-center gap-1.5 rounded-full bg-sky-500/10 px-3 py-1 text-xs font-bold text-sky-400 border border-sky-500/20">
								<RacingIcon name="spark_plug" size="xs" />
								{pilot.sponsor} Sponsor
							</span>
							<span class="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-bold text-emerald-400 border border-emerald-500/20">
								<RacingIcon name="flags" size="xs" />
								{pilot.point} Punti Stagione
							</span>
						</div>
					</div>
				</div>

				<!-- Quick deck status HUD -->
				<div class="flex items-center gap-3 rounded-xl border border-white/10 bg-[#0e121a] p-4">
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/20 text-primary">
						<RacingIcon name="gear" size="md" />
					</div>
					<div>
						<span class="block text-[10px] uppercase font-bold text-muted-foreground tracking-wider">Capienza Mazzo</span>
						<span class="font-racing text-2xl font-black {full ? 'text-amber-400' : 'text-white'}">
							{gameTotal} <span class="text-sm font-normal text-muted-foreground">/ {MAX_GAME_DECK} CARTE</span>
						</span>
					</div>
				</div>
			</div>
		</div>

		{#if locked}
			<div class="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-xs text-amber-200 flex items-center gap-3" role="status">
				<RacingIcon name="flags" size="md" />
				<div>
					<span class="font-bold uppercase tracking-wider block font-racing text-sm text-amber-400">Mazzo in Sola Lettura</span>
					<span>C'è una gara in corso o in attesa di revisione: potrai modificare la configurazione del mazzo dopo la conferma ufficiale.</span>
				</div>
			</div>
		{/if}

		{#if error}
			<div class="rounded-xl border border-destructive/40 bg-destructive/15 p-3 text-xs text-red-300 flex items-center gap-2" role="alert">
				<RacingIcon name="flame" size="xs" />
				<span>{error}</span>
			</div>
		{/if}

		<!-- Deck Builder Layout -->
		<div class="grid gap-6 lg:grid-cols-[minmax(0,5fr)_minmax(0,3fr)] lg:items-start">
			<!-- Game Deck (Pinned on desktop right, top on mobile) -->
			<div class="lg:sticky lg:top-18 lg:order-2 lg:max-h-[calc(100vh-6rem)] lg:overflow-y-auto">
				<div class="overflow-hidden rounded-2xl border border-primary/30 bg-[#121622] shadow-xl curb-top">
					<div class="border-b border-white/10 bg-[#191522] px-5 py-4 flex items-center justify-between">
						<div class="flex items-center gap-2.5">
							<div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/20 text-primary">
								<RacingIcon name="speedometer" size="sm" />
							</div>
							<div>
								<h2 class="font-racing text-2xl font-bold uppercase tracking-wide text-white">
									Mazzo da Gara
								</h2>
								<p class="text-xs text-muted-foreground">
									<span class="{full ? 'font-bold text-amber-400' : 'text-white'} font-racing">
										{gameTotal}/{MAX_GAME_DECK} carte
									</span>
									{#if !locked}
										· clicca per scartare all'inventario
									{/if}
								</p>
							</div>
						</div>
					</div>

					<div class="p-4 sm:p-5">
						{#if pilot.game_deck.length === 0}
							<div class="py-8 text-center text-xs text-muted-foreground italic">
								Il mazzo da gara è vuoto. Clicca sulle carte dell'inventario per caricarle nel motore!
							</div>
						{:else}
							<div class="grid grid-cols-3 sm:grid-cols-4 gap-2.5">
								{#each pilot.game_deck as card (card.path)}
									<CardTile
										{card}
										compact
										disabled={busy || locked}
										title="Copie nel mazzo"
										onclick={() => move(card.path, 'remove')}
									/>
								{/each}
							</div>
						{/if}
					</div>
				</div>
			</div>

			<!-- Inventory Section (Left) -->
			<div class="lg:order-1">
				<div class="overflow-hidden rounded-2xl border border-white/10 bg-[#121622] shadow-xl">
					<div class="relative border-b border-white/10 bg-[#171c28] overflow-hidden">
						<!-- Dashboard/cards photo background -->
						<div class="absolute inset-0 z-0">
							<img
								src="/images/heat-dashboard.webp"
								alt="Heat dashboard con carte"
								class="w-full h-full object-cover object-top opacity-15"
							/>
							<div class="absolute inset-0 bg-gradient-to-r from-[#171c28] via-[#171c28]/90 to-transparent"></div>
						</div>
						<div class="relative z-10 px-5 py-4 flex items-center justify-between">
							<div class="flex items-center gap-2.5">
								<div class="flex h-8 w-8 items-center justify-center rounded-lg bg-white/5 text-amber-400">
									<RacingIcon name="wrenches" size="sm" />
								</div>
								<div>
									<h2 class="font-racing text-2xl font-bold uppercase tracking-wide text-white">
										Inventario Ricambi & Modifiche
									</h2>
									<p class="text-xs text-muted-foreground">
										{#if locked}
											Mazzo bloccato per gara in corso.
										{:else}
											Clicca una carta modifica per caricarla nel mazzo di gara.
										{/if}
									</p>
								</div>
							</div>
						</div>
					</div>

					<div class="p-4 sm:p-5 space-y-6">
						<InventorySection title="Carte Modifica" count={total(pilot.inventory)}>
							{#if pilot.inventory.length === 0}
								<p class="text-xs text-muted-foreground italic py-3">Nessuna carta modifica disponibile.</p>
							{:else}
								<div class="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-6 gap-2.5">
									{#each pilot.inventory as card (card.path)}
										<CardTile
											{card}
											compact
											disabled={busy || full || locked}
											title="Copie in inventario"
											onclick={() => move(card.path, 'add')}
										/>
									{/each}
								</div>
							{/if}
						</InventorySection>

						<div class="border-t border-white/10 pt-5">
							<InventorySection title="Carte Sponsor (Riservate per la Gara)" count={total(pilot.sponsor_inventory)}>
								{#if pilot.sponsor_inventory.length === 0}
									<p class="text-xs text-muted-foreground italic py-3">Nessuna carta sponsor ottenuta.</p>
								{:else}
									<div class="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-6 gap-2.5">
										{#each pilot.sponsor_inventory as card (card.path)}
											<CardTile {card} compact title="Copie in inventario" />
										{/each}
									</div>
								{/if}
							</InventorySection>
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}
</main>