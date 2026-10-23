<script lang="ts">
	import { fetchAdminChampionshipPilots } from '$lib/admin-pilot-cards-api';
	import type { AdminPilotRead } from '$lib/admin-pilot-cards-types';
	import AdminPilotCardsPanel from '$lib/components/admin-pilot-cards-panel.svelte';
	import { Button } from '$lib/components/ui/button';

	let { championshipId }: { championshipId: number } = $props();
	let pilots = $state<AdminPilotRead[]>([]);
	let selectedPilotId = $state<number | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let refresh = $state(0);

	// Le letture appartengono al campionato corrente; la pulizia ignora risposte tardive.
	$effect(() => {
		const championship = championshipId;
		const attempt = refresh;
		let active = true;
		pilots = [];
		selectedPilotId = null;
		error = null;
		loading = true;
		void fetchAdminChampionshipPilots(championship)
			.then((rows) => {
				if (active && attempt === refresh) pilots = rows;
			})
			.catch((cause: unknown) => {
				if (active && attempt === refresh) {
					error = cause instanceof Error ? cause.message : 'Lettura dei piloti non riuscita';
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

<section aria-label="Piloti iscritti" aria-busy={loading} class="space-y-4">
	{#if selectedPilotId !== null}
		<Button variant="outline" onclick={() => (selectedPilotId = null)}>Torna ai piloti</Button>
		{#key `${championshipId}:${selectedPilotId}`}
			<AdminPilotCardsPanel {championshipId} pilotId={selectedPilotId} />
		{/key}
	{:else if loading}
		<p role="status" class="text-sm text-muted-foreground">Caricamento dei piloti…</p>
	{:else if error}
		<p role="alert" class="text-sm text-destructive">{error}</p>
		<Button variant="outline" onclick={() => (refresh += 1)}>Riprova la lettura</Button>
	{:else if pilots.length === 0}
		<p class="text-sm text-muted-foreground">Nessun pilota visibile iscritto al campionato.</p>
	{:else}
		<ul class="space-y-2">
			{#each pilots as pilot (pilot.pilot_id)}
				<li class="flex items-center justify-between gap-3 rounded-lg border p-3">
					<div class="min-w-0">
						<p class="truncate font-medium">{pilot.name}</p>
						<p class="truncate text-sm text-muted-foreground">Utente: {pilot.username}</p>
					</div>
					<Button
						size="sm"
						variant="outline"
						aria-label={`Visualizza le carte di ${pilot.name} (${pilot.username})`}
						onclick={() => (selectedPilotId = pilot.pilot_id)}
					>
						<span aria-hidden="true">🃏</span>
						Carte
					</Button>
				</li>
			{/each}
		</ul>
	{/if}
</section>
