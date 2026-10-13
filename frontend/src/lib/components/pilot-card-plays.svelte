<script lang="ts">
	import { fetchCardPlayState, playCard, undoCard } from '$lib/card-play-api';
	import type { AvailableCard, CardPlay, CardPlayState } from '$lib/card-play-types';
	import type { CardEntry } from '$lib/types';
	import CardTile from '$lib/components/CardTile.svelte';
	import ConfirmDialog from '$lib/components/confirm-dialog.svelte';
	import { Button } from '$lib/components/ui/button';

	// Sezione a scomparsa di un pilota: carte sponsor giocabili e annulla.
	// Il tasto S non è qui: giudice e admin lo trovano nella pagina della gara.
	let {
		championshipId,
		pilot
	}: {
		championshipId: number;
		pilot: { id: number; name: string };
	} = $props();

	let open = $state(false);
	// Non chiamare questa variabile `state`: nasconderebbe la rune $state.
	let cardState = $state<CardPlayState | null>(null);
	let error = $state<string | null>(null);
	let busy = $state(false);
	let confirmOpen = $state(false);
	let pending = $state<AvailableCard | null>(null);

	let activePlays = $derived(
		cardState ? cardState.plays.filter((p: CardPlay) => p.status === 'giocata') : []
	);
	let locked = $derived(busy || cardState === null || cardState.in_review);

	// Converte la carta giocabile nel formato di CardTile: le copie mostrate sono quelle disponibili.
	function toEntry(card: AvailableCard): CardEntry {
		return { name: card.name, path: card.path, copies: card.copies_available };
	}

	// Esegue un'azione sul backend e mostra il messaggio d'errore sotto i pulsanti.
	async function run(action: () => Promise<void>) {
		error = null;
		busy = true;
		try {
			await action();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			busy = false;
		}
	}

	async function load() {
		await run(async () => {
			cardState = await fetchCardPlayState(championshipId, pilot.id);
		});
	}

	function toggle() {
		open = !open;
		if (open) void load();
	}

	function askPlay(card: AvailableCard) {
		pending = card;
		confirmOpen = true;
	}

	async function playPending() {
		const card = pending;
		if (!card) return;
		await run(async () => {
			cardState = await playCard(championshipId, pilot.id, card.name);
		});
	}

	async function undo() {
		await run(async () => {
			cardState = await undoCard(championshipId, pilot.id);
		});
	}
</script>

<section class="rounded-lg border p-3">
	<div class="flex items-center justify-between gap-3">
		<h3 class="font-medium">{pilot.name}</h3>
		<Button size="sm" variant="outline" onclick={toggle} aria-expanded={open}>
			{open ? 'Chiudi' : 'Carte sponsor'}
		</Button>
	</div>

	{#if open}
		<div class="mt-3 space-y-3">
			{#if cardState === null}
				{#if !error}
					<p class="text-sm text-muted-foreground">Caricamento…</p>
				{/if}
			{:else}
				{#if cardState.in_review}
					<p class="text-sm text-muted-foreground">
						La gara è in revisione: non si possono più giocare né annullare carte.
					</p>
				{/if}

				<div class="flex flex-wrap items-center gap-2">
					<Button
						size="sm"
						variant="outline"
						onclick={undo}
						disabled={locked || activePlays.length === 0 || cardState.undo_remaining === 0}
					>
						Annulla ultima ({cardState.undo_remaining} rimasti)
					</Button>
				</div>

				{#if cardState.available.length === 0}
					<p class="text-sm text-muted-foreground">Nessuna carta sponsor nell'inventario.</p>
				{:else}
					<ul class="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
						{#each cardState.available as card (card.name)}
							<li>
								<CardTile
									card={toEntry(card)}
									title="Copie ancora giocabili"
									disabled={locked || card.copies_available < 1}
									onclick={() => askPlay(card)}
								/>
							</li>
						{/each}
					</ul>
				{/if}

				<div>
					<h4 class="mb-1 text-sm font-medium">Giocate in questa gara</h4>
					{#if activePlays.length === 0}
						<p class="text-sm text-muted-foreground">Nessuna carta giocata.</p>
					{:else}
						<ol class="list-decimal pl-5 text-sm">
							{#each activePlays as play (play.id)}
								<li>{play.card_name}</li>
							{/each}
						</ol>
					{/if}
				</div>
			{/if}

			{#if error}
				<p class="text-sm text-destructive" role="alert">{error}</p>
			{/if}
		</div>
	{/if}
</section>

<ConfirmDialog
	bind:open={confirmOpen}
	title="Giocare la carta?"
	message={pending ? `Vuoi giocare «${pending.name}» con ${pilot.name}?` : ''}
	confirmLabel="Gioca"
	onconfirm={playPending}
/>
