<script lang="ts">
	import { fetchAdminPilotCards } from '$lib/admin-pilot-cards-api';
	import type { AdminPilotCardsRead } from '$lib/admin-pilot-cards-types';
	import AdminCardContainer from '$lib/components/admin-card-container.svelte';
	import { Button } from '$lib/components/ui/button';

	let { championshipId, pilotId }: { championshipId: number; pilotId: number } = $props();
	let data = $state<AdminPilotCardsRead | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let refresh = $state(0);

	// Una risposta tardiva non deve ripopolare un pannello chiuso o cambiato.
	$effect(() => {
		const championship = championshipId;
		const pilot = pilotId;
		const attempt = refresh;
		let active = true;
		data = null;
		error = null;
		loading = true;
		void fetchAdminPilotCards(championship, pilot)
			.then((snapshot) => {
				if (active && attempt === refresh) data = snapshot;
			})
			.catch((cause: unknown) => {
				if (active && attempt === refresh) {
					error = cause instanceof Error ? cause.message : 'Lettura delle carte non riuscita';
				}
			})
			.finally(() => {
				if (active && attempt === refresh) loading = false;
			});
		return () => {
			active = false;
		};
	});
</script>

<section aria-label="Carte del pilota" aria-busy={loading} class="space-y-4">
	{#if loading}
		<p role="status" class="text-sm text-muted-foreground">Caricamento delle carte…</p>
	{:else if error}
		<p role="alert" class="text-sm text-destructive">{error}</p>
		<Button variant="outline" onclick={() => (refresh += 1)}>Riprova la lettura</Button>
	{:else if data}
		<div>
			<h3 class="font-semibold">{data.pilot.name}</h3>
			<p class="text-sm text-muted-foreground">Utente: {data.pilot.username}</p>
			<p class="text-sm text-muted-foreground">Modalità consultazione: nessuna modifica alle carte.</p>
		</div>
		{#if data.read_only}
			<p role="status" class="text-sm">{data.blocked_reason ?? 'Modifiche bloccate dal backend'}</p>
		{/if}
		<div class="grid gap-4 md:grid-cols-2">
			<div class="space-y-3">
				<h4 class="font-semibold">Carte del pilota</h4>
				<AdminCardContainer title="Mazzo da gioco" deck={data.containers.game_deck} gameDeck />
				<AdminCardContainer
					title="Inventario Modifiche"
					deck={data.containers.modification_inventory}
				/>
				<AdminCardContainer title="Inventario Sponsor" deck={data.containers.sponsor_inventory} />
			</div>
			<div class="space-y-3">
				<h4 class="font-semibold">Pool del campionato</h4>
				<AdminCardContainer title="Pool Modifiche" deck={data.containers.modification_pool} />
				<AdminCardContainer title="Pool Sponsor" deck={data.containers.sponsor_pool} />
			</div>
		</div>
	{/if}
</section>
