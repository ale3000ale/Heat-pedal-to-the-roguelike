<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import { fetchMyShops, fetchShop } from '$lib/shop/shop-api';
	import { shopSelection } from '$lib/shop/shop-selection.svelte';
	import type { ShopEntry, ShopPilot } from '$lib/shop/shop-types';
	import RacingIcon from '$lib/components/shared/racing-icon.svelte';
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
	<div
		class="flex flex-col justify-between gap-4 border-b border-white/10 pb-5 sm:flex-row sm:items-center"
	>
		<div class="flex items-center gap-3">
			<div
				class="flex h-11 w-11 items-center justify-center rounded-xl border border-sky-500/30 bg-sky-500/20 text-sky-400 shadow-lg"
			>
				<RacingIcon name="tires" size="lg" />
			</div>
			<div>
				<h1
					class="font-racing text-3xl font-black tracking-wide text-white uppercase italic sm:text-4xl"
				>
					OFFICINA RICAMBI & NEGOZIO
				</h1>
				<p class="mt-0.5 text-xs tracking-widest text-muted-foreground uppercase">
					Acquisto pacchetti di potenziamento e carte sponsor
				</p>
			</div>
		</div>
	</div>

	{#if error}
		<div
			class="flex items-center gap-2 rounded-xl border border-destructive/40 bg-destructive/15 p-3 text-xs text-red-300"
			role="alert"
		>
			<RacingIcon name="flame" size="xs" />
			<span>{error}</span>
		</div>
	{:else if shops === null}
		<div class="flex items-center justify-center p-12 text-muted-foreground">
			<RacingIcon name="speedometer" size="lg" class="mr-3 animate-spin text-primary" />
			<span class="font-racing text-lg tracking-wider uppercase">Accesso al magazzino ricambi…</span
			>
		</div>
	{:else if shops.length === 0}
		<!-- Themed Empty State -->
		<div
			class="overflow-hidden rounded-2xl border border-white/10 bg-[#121622] p-8 text-center shadow-xl sm:p-12"
		>
			<div
				class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl border border-sky-500/20 bg-sky-500/10 text-sky-400"
			>
				<RacingIcon name="spark_plug" size="xl" />
			</div>
			<h3 class="font-racing text-2xl font-bold tracking-wider text-white uppercase">
				Nessuna officina attiva
			</h3>
			<p class="mx-auto mt-2 max-w-md text-xs text-muted-foreground sm:text-sm">
				Non stai partecipando a nessun campionato attivo con un tuo pilota iscritto. Per accedere al
				negozio e spendere l'oro accumulato, iscrivi un pilota a un campionato.
			</p>
			<div class="mt-6 flex justify-center gap-3">
				<a href={resolve('/championships')}>
					<Button
						class="heat-glow h-10 bg-primary px-6 font-racing text-base font-bold tracking-wider text-white uppercase hover:bg-accent"
					>
						<RacingIcon name="trophy" size="sm" class="mr-2" />
						Iscriviti a un Campionato
					</Button>
				</a>
			</div>
		</div>
	{:else}
		<div class="grid gap-6 sm:grid-cols-2">
			{#each shops as shop (shop.championship_id)}
				<div
					class="curb-left overflow-hidden rounded-2xl border border-white/10 bg-[#141824] shadow-xl"
				>
					<div
						class="flex items-center justify-between border-b border-white/10 bg-[#181d2a] px-5 py-4"
					>
						<div>
							<h3 class="font-racing text-2xl font-bold tracking-wide text-white uppercase">
								{shop.championship_name}
							</h3>
							<p class="mt-0.5 text-xs text-muted-foreground">
								Seleziona il pilota per accedere all'inventario
							</p>
						</div>
						<div
							class="flex h-9 w-9 items-center justify-center rounded-lg bg-white/5 text-amber-400"
						>
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
										class="group flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/5 bg-[#0e121a] p-3.5 transition-all hover:border-primary/40 hover:bg-[#151a24]"
									>
										<div class="flex items-center gap-3">
											<div class="racing-roundel h-7 w-7 shrink-0 text-xs">
												#{pilot.id}
											</div>
											<span class="group-hover:text-heat font-bold text-white transition-colors">
												{pilot.name}
											</span>
										</div>

										<div class="flex items-center gap-2">
											{#if balance}
												<span
													class="inline-flex items-center gap-1 rounded-full border border-amber-500/20 bg-amber-500/10 px-2.5 py-0.5 text-xs font-bold text-amber-400"
												>
													<RacingIcon name="trophy" size="xs" />
													{balance.gold} Oro
												</span>
												<span
													class="inline-flex items-center gap-1 rounded-full border border-sky-500/20 bg-sky-500/10 px-2.5 py-0.5 text-xs font-bold text-sky-400"
												>
													<RacingIcon name="spark_plug" size="xs" />
													{balance.sponsor} Sponsor
												</span>
											{:else}
												<span class="text-xs text-muted-foreground">Caricamento crediti…</span>
											{/if}
											<span
												class="ml-1 text-xs font-bold text-primary transition-transform group-hover:translate-x-1"
												>→</span
											>
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
