<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import { fetchMyShops, fetchShop } from '$lib/shop-api';
	import { shopSelection } from '$lib/shop-selection.svelte';
	import type { ShopEntry, ShopPilot } from '$lib/shop-types';
	import * as Card from '$lib/components/ui/card';
	import RacingIcon from '$lib/components/racing-icon.svelte';
	import { Button } from '$lib/components/ui/button';

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

<svelte:head><title>Officina & Negozio Upgrade — Heat</title></svelte:head>

<main class="mx-auto max-w-6xl space-y-6 px-4 py-8 sm:px-6">
	<!-- Page Header Banner -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5">
		<div class="flex items-center gap-3">
			<div class="flex h-11 w-11 items-center justify-center rounded-xl bg-sky-500/20 border border-sky-500/30 text-sky-400 shadow-lg">
				<RacingIcon name="tires" size="lg" />
			</div>
			<div>
				<h1 class="font-racing text-3xl sm:text-4xl font-black uppercase italic tracking-wide text-white">
					OFFICINA RICAMBI & NEGOZIO
				</h1>
				<p class="text-xs text-muted-foreground uppercase tracking-widest mt-0.5">
					Acquisto pacchetti di potenziamento e carte sponsor
				</p>
			</div>
		</div>
	</div>

	{#if error}
		<div class="rounded-xl border border-destructive/40 bg-destructive/15 p-3 text-xs text-red-300 flex items-center gap-2" role="alert">
			<RacingIcon name="flame" size="xs" />
			<span>{error}</span>
		</div>
	{:else if shops === null}
		<div class="flex items-center justify-center p-12 text-muted-foreground">
			<RacingIcon name="speedometer" size="lg" class="animate-spin mr-3 text-primary" />
			<span class="font-racing text-lg uppercase tracking-wider">Accesso al magazzino ricambi…</span>
		</div>
	{:else if shops.length === 0}
		<!-- Themed Empty State -->
		<div class="overflow-hidden rounded-2xl border border-white/10 bg-[#121622] p-8 sm:p-12 text-center shadow-xl">
			<div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-sky-500/10 border border-sky-500/20 text-sky-400">
				<RacingIcon name="spark_plug" size="xl" />
			</div>
			<h3 class="font-racing text-2xl font-bold uppercase tracking-wider text-white">Nessuna officina attiva</h3>
			<p class="mt-2 text-xs sm:text-sm text-muted-foreground max-w-md mx-auto">
				Non stai partecipando a nessun campionato attivo con un tuo pilota iscritto. Per accedere al negozio e spendere l'oro accumulato, iscrivi un pilota a un campionato.
			</p>
			<div class="mt-6 flex justify-center gap-3">
				<a href={resolve('/championships')}>
					<Button class="bg-primary hover:bg-accent text-white font-racing text-base font-bold uppercase tracking-wider px-6 h-10 heat-glow">
						<RacingIcon name="trophy" size="sm" class="mr-2" />
						Iscriviti a un Campionato
					</Button>
				</a>
			</div>
		</div>
	{:else}
		<div class="grid gap-6 sm:grid-cols-2">
			{#each shops as shop (shop.championship_id)}
				<div class="overflow-hidden rounded-2xl border border-white/10 bg-[#141824] shadow-xl curb-left">
					<div class="border-b border-white/10 bg-[#181d2a] px-5 py-4 flex items-center justify-between">
						<div>
							<h3 class="font-racing text-2xl font-bold uppercase tracking-wide text-white">
								{shop.championship_name}
							</h3>
							<p class="text-xs text-muted-foreground mt-0.5">Seleziona il pilota per accedere all'inventario</p>
						</div>
						<div class="flex h-9 w-9 items-center justify-center rounded-lg bg-white/5 text-amber-400">
							<RacingIcon name="trophy" size="sm" />
						</div>
					</div>

					<div class="p-4 sm:p-5">
						<ul class="space-y-2.5">
							{#each shop.pilots as pilot (pilot.id)}
								{@const balance = balances[pilot.id]}
								<li>
									<a
										href={resolve('/championships/[id]/shop', {
											id: String(shop.championship_id)
										})}
										onclick={() => (shopSelection.pilotId = pilot.id)}
										class="flex flex-wrap items-center justify-between gap-3 rounded-xl bg-[#0e121a] border border-white/5 p-3.5 hover:border-primary/40 hover:bg-[#151a24] transition-all group"
									>
										<div class="flex items-center gap-3">
											<div class="racing-roundel h-7 w-7 text-xs shrink-0">
												#{pilot.id}
											</div>
											<span class="font-bold text-white group-hover:text-heat transition-colors">
												{pilot.name}
											</span>
										</div>

										<div class="flex items-center gap-2">
											{#if balance}
												<span class="inline-flex items-center gap-1 rounded-full bg-amber-500/10 px-2.5 py-0.5 text-xs font-bold text-amber-400 border border-amber-500/20">
													<RacingIcon name="trophy" size="xs" />
													{balance.gold} Oro
												</span>
												<span class="inline-flex items-center gap-1 rounded-full bg-sky-500/10 px-2.5 py-0.5 text-xs font-bold text-sky-400 border border-sky-500/20">
													<RacingIcon name="spark_plug" size="xs" />
													{balance.sponsor} Sponsor
												</span>
											{:else}
												<span class="text-xs text-muted-foreground">Caricamento crediti…</span>
											{/if}
											<span class="text-xs font-bold text-primary group-hover:translate-x-1 transition-transform ml-1">→</span>
										</div>
									</a>
								</li>
							{/each}
						</ul>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</main>
