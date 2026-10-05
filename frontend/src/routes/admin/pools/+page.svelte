<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import { api } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import type { CardEntry, Pool, PoolDetail, PoolKind, ReloadResult } from '$lib/types';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';

	const kinds: PoolKind[] = ['modifiche', 'sponsor'];
	const kindLabels: Record<PoolKind, string> = { modifiche: 'Modifiche', sponsor: 'Sponsor' };
	// Nomi delle pool di base nel backend.
	const baseNames: Record<PoolKind, string> = { modifiche: 'default', sponsor: 'sponsor' };

	let pools = $state<Pool[]>([]);
	let error = $state<string | null>(null);
	let actionError = $state<string | null>(null);
	let formError = $state<string | null>(null);
	let busy = $state<string | null>(null);
	let loaded = $state(false);
	let results = $state<Partial<Record<PoolKind, ReloadResult>>>({});

	// Modulo di creazione: tipo, nome, carte della base e copie scelte per ciascuna.
	let newKind = $state<PoolKind>('modifiche');
	let newName = $state('');
	let baseCards = $state<CardEntry[]>([]);
	let picks = $state<Record<string, number>>({});

	let derived = $derived(pools.filter((pool) => pool.name !== baseNames[pool.kind]));

	function message(e: unknown): string {
		return e instanceof Error ? e.message : 'Errore sconosciuto';
	}

	function baseOf(kind: PoolKind): Pool | undefined {
		return pools.find((pool) => pool.kind === kind && pool.name === baseNames[kind]);
	}

	async function loadPools() {
		pools = await api<Pool[]>('/pools');
	}

	// Carica le carte della pool di base del tipo scelto e azzera le scelte.
	async function loadBaseCards() {
		picks = {};
		const base = baseOf(newKind);
		if (!base) {
			baseCards = [];
			return;
		}
		const detail = await api<PoolDetail>(`/pools/${base.id}`);
		baseCards = detail.cards;
	}

	onMount(async () => {
		if (!auth.isAdmin) {
			loaded = true;
			return;
		}
		try {
			await loadPools();
			await loadBaseCards();
		} catch (e) {
			error = message(e);
		} finally {
			loaded = true;
		}
	});

	async function chooseKind(kind: PoolKind) {
		newKind = kind;
		formError = null;
		try {
			await loadBaseCards();
		} catch (e) {
			formError = message(e);
		}
	}

	// Legge i file della cartella e aggiunge soltanto le carte nuove.
	async function reload(kind: PoolKind) {
		actionError = null;
		busy = `reload-${kind}`;
		try {
			const result = await api<ReloadResult>(`/pools/base/${kind}/reload`, { method: 'POST' });
			results = { ...results, [kind]: result };
			await loadPools();
			if (kind === newKind) await loadBaseCards();
		} catch (e) {
			actionError = message(e);
		} finally {
			busy = null;
		}
	}

	async function remove(pool: Pool) {
		if (!confirm(`Eliminare la pool "${pool.name}"?`)) return;
		actionError = null;
		busy = `delete-${pool.id}`;
		try {
			await api(`/pools/${pool.id}`, { method: 'DELETE' });
			await loadPools();
		} catch (e) {
			actionError = message(e);
		} finally {
			busy = null;
		}
	}

	// Tiene il numero di copie tra 0 e le copie della pool di base.
	function setPick(card: CardEntry, value: number) {
		const copies = Number.isFinite(value)
			? Math.min(Math.max(Math.trunc(value), 0), card.copies)
			: 0;
		picks = { ...picks, [card.name]: copies };
	}

	async function create(event: SubmitEvent) {
		event.preventDefault();
		formError = null;
		const cards = baseCards
			.filter((card) => (picks[card.name] ?? 0) > 0)
			.map((card) => ({ name: card.name, copies: picks[card.name] }));
		if (cards.length === 0) {
			formError = 'Scegli almeno una carta';
			return;
		}
		busy = 'create';
		try {
			await api('/pools', { method: 'POST', body: { name: newName, kind: newKind, cards } });
			newName = '';
			picks = {};
			await loadPools();
		} catch (e) {
			formError = message(e);
		} finally {
			busy = null;
		}
	}
</script>

<svelte:head><title>Pool - Heat</title></svelte:head>

<main class="mx-auto max-w-5xl space-y-6 p-6">
	<a href={resolve('/')} class="text-sm text-muted-foreground hover:text-foreground"> ← Home </a>

	<h1 class="text-2xl font-bold">Pool di carte</h1>

	{#if !loaded}
		<p class="text-muted-foreground">Caricamento…</p>
	{:else if !auth.isAdmin}
		<p class="text-sm text-destructive" role="alert">Questa pagina è riservata all'admin.</p>
	{:else if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{:else}
		<Card.Root>
			<Card.Header>
				<Card.Title>Pool di base</Card.Title>
				<Card.Description>
					«Ricarica» legge i file della cartella e aggiunge solo le carte nuove: non modifica né
					toglie quelle già presenti.
				</Card.Description>
			</Card.Header>
			<Card.Content>
				<ul class="divide-y">
					{#each kinds as kind (kind)}
						{@const base = baseOf(kind)}
						{@const result = results[kind]}
						<li class="py-3">
							<div class="flex items-center gap-3">
								{#if base}
									<a
										href={resolve('/admin/pools/[id]', { id: String(base.id) })}
										class="flex-1 font-medium hover:underline"
									>
										{kindLabels[kind]}
									</a>
									<span class="text-sm text-muted-foreground">
										{base.cards_count} carte · {base.copies_count} copie
									</span>
									<Button
										size="sm"
										variant="outline"
										disabled={busy === `reload-${kind}`}
										onclick={() => reload(kind)}
									>
										Ricarica
									</Button>
								{:else}
									<span class="flex-1 font-medium">{kindLabels[kind]}</span>
									<span class="text-sm text-muted-foreground">Pool di base assente</span>
								{/if}
							</div>
							{#if result}
								<div class="mt-2 space-y-1 text-sm" role="status">
									<p>
										Aggiunte: {result.added.length}, già presenti: {result.already_present}.
									</p>
									{#if result.added.length > 0}
										<p class="text-muted-foreground">{result.added.join(', ')}</p>
									{/if}
									{#each result.warnings as warning (warning)}
										<p class="text-destructive">{warning}</p>
									{/each}
								</div>
							{/if}
						</li>
					{/each}
				</ul>
				{#if actionError}
					<p class="mt-3 text-sm text-destructive" role="alert">{actionError}</p>
				{/if}
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Header>
				<Card.Title>Pool create</Card.Title>
				<Card.Description>Clicca su una pool per aprirla.</Card.Description>
			</Card.Header>
			<Card.Content>
				{#if derived.length === 0}
					<p class="text-sm text-muted-foreground">Nessuna pool creata.</p>
				{:else}
					<ul class="divide-y">
						{#each derived as pool (pool.id)}
							<li class="flex items-center gap-3 py-2">
								<a
									href={resolve('/admin/pools/[id]', { id: String(pool.id) })}
									class="flex-1 font-medium hover:underline"
								>
									{pool.name}
								</a>
								<span class="text-sm text-muted-foreground">{kindLabels[pool.kind]}</span>
								<span class="text-sm text-muted-foreground">
									{pool.cards_count} carte · {pool.copies_count} copie
								</span>
								<Button
									size="sm"
									variant="outline"
									disabled={busy === `delete-${pool.id}`}
									onclick={() => remove(pool)}
								>
									Elimina
								</Button>
							</li>
						{/each}
					</ul>
				{/if}
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Header>
				<Card.Title>Nuova pool</Card.Title>
				<Card.Description>
					Scegli il tipo, poi quante copie tenere di ogni carta della pool di base (da 0 al massimo
					disponibile).
				</Card.Description>
			</Card.Header>
			<Card.Content>
				<form class="space-y-4" onsubmit={create}>
					<div class="flex gap-2">
						{#each kinds as kind (kind)}
							<Button
								type="button"
								size="sm"
								variant={newKind === kind ? 'default' : 'outline'}
								onclick={() => chooseKind(kind)}
							>
								{kindLabels[kind]}
							</Button>
						{/each}
					</div>

					<label class="block space-y-1 text-sm">
						<span>Nome</span>
						<input
							class="h-9 w-full rounded-md border bg-background px-3 text-sm"
							bind:value={newName}
							minlength={2}
							maxlength={40}
							required
						/>
					</label>

					{#if baseCards.length === 0}
						<p class="text-sm text-muted-foreground">
							La pool di base è vuota: usa «Ricarica» per leggere le carte dalla cartella.
						</p>
					{:else}
						<ul class="divide-y">
							{#each baseCards as card (card.path)}
								<li class="flex items-center gap-3 py-2">
									<span class="flex-1">{card.name}</span>
									<span class="text-sm text-muted-foreground">max {card.copies}</span>
									<input
										type="number"
										class="h-9 w-20 rounded-md border bg-background px-2 text-sm"
										min={0}
										max={card.copies}
										aria-label={`Copie di ${card.name}`}
										value={picks[card.name] ?? 0}
										oninput={(e) => setPick(card, e.currentTarget.valueAsNumber)}
									/>
								</li>
							{/each}
						</ul>
					{/if}

					{#if formError}
						<p class="text-sm text-destructive" role="alert">{formError}</p>
					{/if}
					<Button type="submit" disabled={busy === 'create' || baseCards.length === 0}>
						Crea pool
					</Button>
				</form>
			</Card.Content>
		</Card.Root>
	{/if}
</main>
