<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import { api } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import type { Championship, Pool } from '$lib/types';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';

	let championships = $state<Championship[]>([]);
	let pools = $state<Pool[]>([]);
	let error = $state<string | null>(null);
	let actionError = $state<string | null>(null);
	let formError = $state<string | null>(null);
	let busy = $state<string | null>(null);
	let loaded = $state(false);

	// Modulo di creazione: nome e id (come testo) delle due pool scelte.
	let name = $state('');
	let poolId = $state('');
	let sponsorId = $state('');

	let modifichePools = $derived(pools.filter((pool) => pool.kind === 'modifiche'));
	let sponsorPools = $derived(pools.filter((pool) => pool.kind === 'sponsor'));

	function message(e: unknown): string {
		return e instanceof Error ? e.message : 'Errore sconosciuto';
	}

	function formatDate(value: string): string {
		return new Date(value).toLocaleDateString('it-IT');
	}

	function describe(pool: Pool): string {
		return `${pool.name} (${pool.cards_count} carte, ${pool.copies_count} copie)`;
	}

	async function loadChampionships() {
		championships = await api<Championship[]>('/championships');
	}

	// Preseleziona la pool di base di ciascun tipo, se non è già stata scelta una pool.
	function presetPools() {
		if (!poolId) {
			const base = modifichePools.find((pool) => pool.name === 'default') ?? modifichePools[0];
			poolId = base ? String(base.id) : '';
		}
		if (!sponsorId) {
			const base = sponsorPools.find((pool) => pool.name === 'sponsor') ?? sponsorPools[0];
			sponsorId = base ? String(base.id) : '';
		}
	}

	onMount(async () => {
		if (!auth.isAdmin) {
			loaded = true;
			return;
		}
		try {
			await loadChampionships();
			pools = await api<Pool[]>('/pools');
			presetPools();
		} catch (e) {
			error = message(e);
		} finally {
			loaded = true;
		}
	});

	async function create(event: SubmitEvent) {
		event.preventDefault();
		formError = null;
		busy = 'create';
		try {
			await api('/championships', {
				method: 'POST',
				body: {
					name,
					pool_id: poolId ? Number(poolId) : null,
					sponsor_pool_id: sponsorId ? Number(sponsorId) : null
				}
			});
			name = '';
			await loadChampionships();
		} catch (e) {
			formError = message(e);
		} finally {
			busy = null;
		}
	}

	async function close(championship: Championship) {
		if (!confirm(`Chiudere il campionato "${championship.name}"?`)) return;
		actionError = null;
		busy = `close-${championship.id}`;
		try {
			const updated = await api<Championship>(`/championships/${championship.id}/close`, {
				method: 'POST'
			});
			championships = championships.map((c) => (c.id === updated.id ? updated : c));
		} catch (e) {
			actionError = message(e);
		} finally {
			busy = null;
		}
	}

	async function remove(championship: Championship) {
		if (
			!confirm(
				`Cancellare il campionato "${championship.name}" con tutto lo storico? L'azione non si può annullare.`
			)
		)
			return;
		actionError = null;
		busy = `delete-${championship.id}`;
		try {
			await api(`/championships/${championship.id}`, { method: 'DELETE' });
			await loadChampionships();
		} catch (e) {
			actionError = message(e);
		} finally {
			busy = null;
		}
	}
</script>

<svelte:head><title>Gestione campionati - Heat</title></svelte:head>

<main class="mx-auto max-w-5xl space-y-6 p-6">
	<a href={resolve('/')} class="text-sm text-muted-foreground hover:text-foreground"> ← Home </a>

	<h1 class="text-2xl font-bold">Gestione campionati</h1>

	{#if !loaded}
		<p class="text-muted-foreground">Caricamento…</p>
	{:else if !auth.isAdmin}
		<p class="text-sm text-destructive" role="alert">Questa pagina è riservata all'admin.</p>
	{:else if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{:else}
		<Card.Root>
			<Card.Header>
				<Card.Title>Nuovo campionato</Card.Title>
				<Card.Description>
					Ogni campionato riceve una copia indipendente delle due pool scelte.
				</Card.Description>
			</Card.Header>
			<Card.Content>
				<form class="space-y-4" onsubmit={create}>
					<label class="block space-y-1 text-sm">
						<span>Nome</span>
						<input
							class="h-9 w-full rounded-md border bg-background px-3 text-sm"
							bind:value={name}
							minlength={2}
							maxlength={40}
							required
						/>
					</label>

					<label class="block space-y-1 text-sm">
						<span>Pool delle modifiche</span>
						<select
							class="h-9 w-full rounded-md border bg-background px-3 text-sm"
							bind:value={poolId}
						>
							{#each modifichePools as pool (pool.id)}
								<option value={String(pool.id)}>{describe(pool)}</option>
							{/each}
						</select>
					</label>

					<label class="block space-y-1 text-sm">
						<span>Pool degli sponsor</span>
						<select
							class="h-9 w-full rounded-md border bg-background px-3 text-sm"
							bind:value={sponsorId}
						>
							<option value="">Nessuna</option>
							{#each sponsorPools as pool (pool.id)}
								<option value={String(pool.id)}>{describe(pool)}</option>
							{/each}
						</select>
					</label>

					{#if formError}
						<p class="text-sm text-destructive" role="alert">{formError}</p>
					{/if}
					<Button type="submit" disabled={busy === 'create'}>Crea campionato</Button>
				</form>
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Header>
				<Card.Title>Campionati</Card.Title>
				<Card.Description>
					Un campionato attivo si può chiudere; solo uno chiuso si può cancellare, con tutto lo
					storico.
				</Card.Description>
			</Card.Header>
			<Card.Content>
				{#if championships.length === 0}
					<p class="text-sm text-muted-foreground">Nessun campionato.</p>
				{:else}
					<ul class="divide-y">
						{#each championships as c (c.id)}
							<li class="flex items-center gap-3 py-2">
								<a
									href={resolve('/championships/[id]', { id: String(c.id) })}
									class="flex-1 font-medium hover:underline"
								>
									{c.name}
								</a>
								<span class="text-sm text-muted-foreground">
									{formatDate(c.date)} · {c.pilots_count}
									{c.pilots_count === 1 ? 'pilota' : 'piloti'} · {c.is_closed
										? 'chiuso'
										: 'attivo'}
								</span>
								{#if c.is_closed}
									<Button
										size="sm"
										variant="outline"
										disabled={busy === `delete-${c.id}`}
										onclick={() => remove(c)}
									>
										Cancella
									</Button>
								{:else}
									<Button
										size="sm"
										variant="outline"
										disabled={busy === `close-${c.id}`}
										onclick={() => close(c)}
									>
										Chiudi
									</Button>
								{/if}
							</li>
						{/each}
					</ul>
				{/if}
				{#if actionError}
					<p class="mt-3 text-sm text-destructive" role="alert">{actionError}</p>
				{/if}
			</Card.Content>
		</Card.Root>
	{/if}
</main>
