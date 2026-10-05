<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { api } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import type { CardEntry, PoolDetail } from '$lib/types';

	let pool = $state<PoolDetail | null>(null);
	let error = $state<string | null>(null);
	let loaded = $state(false);
	let saving = $state<string | null>(null);
	// Nome in modifica e ultimo errore, per carta (si usa il percorso, che non cambia).
	let drafts = $state<Record<string, string>>({});
	let cardErrors = $state<Record<string, string>>({});

	function message(e: unknown): string {
		return e instanceof Error ? e.message : 'Errore sconosciuto';
	}

	onMount(async () => {
		if (!auth.isAdmin) {
			loaded = true;
			return;
		}
		try {
			pool = await api<PoolDetail>(`/pools/${page.params.id}`);
		} catch (e) {
			error = message(e);
		} finally {
			loaded = true;
		}
	});

	function setDraft(card: CardEntry, value: string) {
		drafts = { ...drafts, [card.path]: value };
	}

	function clearState(path: string) {
		const { [path]: _draft, ...restDrafts } = drafts;
		drafts = restDrafts;
		const { [path]: _error, ...restErrors } = cardErrors;
		cardErrors = restErrors;
	}

	// Salva il nome quando l'utente esce dal campo o preme Invio.
	async function save(card: CardEntry) {
		if (!pool || saving) return;
		const name = (drafts[card.path] ?? card.name).trim();
		if (name === card.name) {
			clearState(card.path);
			return;
		}
		saving = card.path;
		try {
			pool = await api<PoolDetail>(`/pools/${pool.id}/cards`, {
				method: 'PATCH',
				body: { path: card.path, name }
			});
			clearState(card.path);
		} catch (e) {
			cardErrors = { ...cardErrors, [card.path]: message(e) };
		} finally {
			saving = null;
		}
	}

	function onKey(event: KeyboardEvent & { currentTarget: HTMLInputElement }) {
		if (event.key === 'Enter') event.currentTarget.blur();
	}
</script>

<svelte:head><title>{pool ? pool.name : 'Pool'} - Heat</title></svelte:head>

<main class="mx-auto max-w-5xl space-y-6 p-6">
	<a href={resolve('/admin/pools')} class="text-sm text-muted-foreground hover:text-foreground">
		← Pool di carte
	</a>

	{#if !loaded}
		<p class="text-muted-foreground">Caricamento…</p>
	{:else if !auth.isAdmin}
		<p class="text-sm text-destructive" role="alert">Questa pagina è riservata all'admin.</p>
	{:else if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{:else if pool}
		<div>
			<h1 class="text-2xl font-bold">{pool.name}</h1>
			<p class="text-sm text-muted-foreground">
				{pool.kind === 'sponsor' ? 'Sponsor' : 'Modifiche'} · {pool.cards_count} carte · {pool.copies_count}
				copie
			</p>
		</div>

		{#if pool.cards.length === 0}
			<p class="text-sm text-muted-foreground">Nessuna carta in questa pool.</p>
		{:else}
			<ul class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
				{#each pool.cards as card (card.path)}
					<li class="space-y-2">
						<div class="relative overflow-hidden rounded-md border">
							<img
								src={`/media/${card.path}`}
								alt={card.name}
								loading="lazy"
								class="block w-full"
							/>
							<span
								class="absolute right-2 bottom-2 rounded bg-black/70 px-2 py-0.5 text-sm font-bold text-white"
							>
								×{card.copies}
							</span>
						</div>
						<input
							class="h-9 w-full rounded-md border bg-background px-2 text-sm"
							aria-label={`Nome della carta ${card.name}`}
							maxlength={60}
							value={drafts[card.path] ?? card.name}
							disabled={saving === card.path}
							oninput={(e) => setDraft(card, e.currentTarget.value)}
							onblur={() => save(card)}
							onkeydown={onKey}
						/>
						{#if cardErrors[card.path]}
							<p class="text-xs text-destructive" role="alert">{cardErrors[card.path]}</p>
						{/if}
					</li>
				{/each}
			</ul>
		{/if}
	{/if}
</main>
