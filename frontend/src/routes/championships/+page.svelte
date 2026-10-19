<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import { api } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import { groupChampionships, initiallyOpenGroup, type GroupKey } from '$lib/championship-groups';
	import type { Championship, Pilot } from '$lib/types';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import ChampionshipSettings from '$lib/components/championship-settings.svelte';
	import NewChampionshipDialog from '$lib/components/new-championship-dialog.svelte';

	// Messaggio mostrato quando una sezione non contiene campionati.
	const emptyMessages: Record<GroupKey, string> = {
		enrolled: 'Nessun campionato a cui sei iscritto.',
		active: 'Nessun campionato attivo.',
		closed: 'Nessun campionato chiuso.'
	};

	let championships = $state<Championship[]>([]);
	let pilots = $state<Pilot[]>([]);
	let loaded = $state(false);
	let error = $state<string | null>(null);
	let selectedId = $state<number | null>(null);
	let settingsOpen = $state(false);
	let newOpen = $state(false);
	let openGroups = $state<Record<GroupKey, boolean>>({
		enrolled: false,
		active: false,
		closed: false
	});

	let groups = $derived(groupChampionships(championships, pilots));
	let selected = $derived(championships.find((c) => c.id === selectedId) ?? null);

	// Carica campionati e piloti dell'utente loggato: servono entrambi per la sezione Iscritto.
	async function loadChampionships() {
		[championships, pilots] = await Promise.all([
			api<Championship[]>('/championships'),
			api<Pilot[]>('/pilots')
		]);
	}

	onMount(async () => {
		try {
			await loadChampionships();
			// Una sola sezione aperta all'arrivo; dopo, l'utente apre e chiude come preferisce.
			openGroups[initiallyOpenGroup(groups)] = true;
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

{#snippet section(key: GroupKey, title: string, items: Championship[])}
	<details class="rounded-lg border p-4" bind:open={openGroups[key]}>
		<summary class="cursor-pointer text-lg font-semibold select-none">
			{title} ({items.length})
		</summary>
		<div class="mt-3">
			{@render list(items, emptyMessages[key])}
		</div>
	</details>
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
		{@render section('enrolled', 'Iscritto', groups.enrolled)}
		{@render section('active', 'Attivi', groups.active)}
		{@render section('closed', 'Chiusi', groups.closed)}
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
