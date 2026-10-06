<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import { api } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import type { Championship } from '$lib/types';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import ChampionshipSettings from '$lib/components/championship-settings.svelte';
	import NewChampionshipDialog from '$lib/components/new-championship-dialog.svelte';

	let championships = $state<Championship[]>([]);
	let loaded = $state(false);
	let error = $state<string | null>(null);
	let selectedId = $state<number | null>(null);
	let settingsOpen = $state(false);
	let newOpen = $state(false);

	let active = $derived(championships.filter((c) => !c.is_closed));
	let closed = $derived(championships.filter((c) => c.is_closed));
	let selected = $derived(championships.find((c) => c.id === selectedId) ?? null);

	async function loadChampionships() {
		championships = await api<Championship[]>('/championships');
	}

	onMount(async () => {
		try {
			await loadChampionships();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			loaded = true;
		}
	});

	function formatDate(value: string): string {
		return new Date(value).toLocaleDateString('it-IT');
	}

	function openSettings(championship: Championship) {
		selectedId = championship.id;
		settingsOpen = true;
	}

	function replaceChampionship(updated: Championship) {
		championships = championships.map((c) => (c.id === updated.id ? updated : c));
	}
</script>

<svelte:head><title>Campionati - Heat</title></svelte:head>

{#snippet list(items: Championship[], empty: string)}
	{#if items.length === 0}
		<p class="text-sm text-muted-foreground">{empty}</p>
	{:else}
		<div class="grid gap-4 sm:grid-cols-2">
			{#each items as c (c.id)}
				<div class="relative">
					<a href={resolve('/championships/[id]', { id: String(c.id) })}>
						<Card.Root class="transition-colors hover:bg-accent">
							<Card.Header>
								<Card.Title>{c.name}</Card.Title>
								<Card.Description>
									{formatDate(c.date)} · {c.pilots_count}
									{c.pilots_count === 1 ? 'pilota' : 'piloti'}
								</Card.Description>
							</Card.Header>
						</Card.Root>
					</a>
					{#if auth.isAdmin}
						<Button
							class="absolute top-3 right-3"
							size="sm"
							variant="outline"
							aria-label={`Impostazioni di ${c.name}`}
							onclick={() => openSettings(c)}
						>
							⚙
						</Button>
					{/if}
				</div>
			{/each}
		</div>
	{/if}
{/snippet}

<main class="mx-auto max-w-5xl space-y-6 p-6">
	<div class="flex items-center justify-between gap-3">
		<h1 class="text-2xl font-bold">Campionati</h1>
		{#if auth.isAdmin}
			<Button
				size="sm"
				variant="outline"
				aria-label="Nuovo campionato"
				onclick={() => (newOpen = true)}
			>
				+
			</Button>
		{/if}
	</div>

	{#if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{:else if !loaded}
		<p class="text-muted-foreground">Caricamento…</p>
	{:else}
		<section class="space-y-3">
			<h2 class="text-lg font-semibold">Attivi</h2>
			{@render list(active, 'Nessun campionato attivo.')}
		</section>

		<section class="space-y-3">
			<h2 class="text-lg font-semibold">Chiusi</h2>
			{@render list(closed, 'Nessun campionato chiuso.')}
		</section>
	{/if}

	{#if auth.isAdmin}
		<ChampionshipSettings
			championship={selected}
			bind:open={settingsOpen}
			onclosed={replaceChampionship}
			ondeleted={loadChampionships}
		/>
		<NewChampionshipDialog bind:open={newOpen} oncreated={loadChampionships} />
	{/if}
</main>
