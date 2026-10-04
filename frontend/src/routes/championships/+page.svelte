<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import { api } from '$lib/api';
	import type { Championship } from '$lib/types';
	import * as Card from '$lib/components/ui/card';

	let championships = $state<Championship[]>([]);
	let loaded = $state(false);
	let error = $state<string | null>(null);

	let active = $derived(championships.filter((c) => !c.is_closed));
	let closed = $derived(championships.filter((c) => c.is_closed));

	onMount(async () => {
		try {
			championships = await api<Championship[]>('/championships');
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			loaded = true;
		}
	});

	function formatDate(value: string): string {
		return new Date(value).toLocaleDateString('it-IT');
	}
</script>

<svelte:head><title>Campionati - Heat</title></svelte:head>

{#snippet list(items: Championship[], empty: string)}
	{#if items.length === 0}
		<p class="text-sm text-muted-foreground">{empty}</p>
	{:else}
		<div class="grid gap-4 sm:grid-cols-2">
			{#each items as c (c.id)}
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
			{/each}
		</div>
	{/if}
{/snippet}

<main class="mx-auto max-w-5xl space-y-6 p-6">
	<h1 class="text-2xl font-bold">Campionati</h1>

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
</main>
