<script lang="ts">
	import { onMount } from 'svelte';
	import { errorMessage } from '$lib/admin/shop-admin-format';
	import {
		boardPoolImageUrl,
		fetchBoardPool,
		updateBoardPoolCard,
		type BoardPool,
		type BoardPoolCard,
		type BoardPoolCardPatch,
		type BoardPoolKind
	} from '$lib/championship/board-pool-api';
	import { Button } from '$lib/components/ui/button';
	import ConfirmDialog from '$lib/components/shared/confirm-dialog.svelte';
	import RacingIcon from '$lib/components/shared/racing-icon.svelte';

	// Pool di mappe o eventi del campionato: tutte le carte del catalogo, con lo
	// stato in pool / fuori pool. Le carte sono orizzontali: nome sopra, immagine
	// e informazioni sotto; quelle fuori pool sono scure, semi-trasparenti e
	// contrassegnate dall'icona rossa.
	let {
		championshipId,
		kind,
		onback
	}: { championshipId: number; kind: BoardPoolKind; onback?: () => void } = $props();

	type PendingChange = {
		card: BoardPoolCard;
		patch: BoardPoolCardPatch;
		title: string;
		message: string;
		confirmLabel: string;
	};

	let pool = $state<BoardPool | null>(null);
	let error = $state<string | null>(null);
	let actionError = $state<string | null>(null);
	let pending = $state<PendingChange | null>(null);
	let confirmOpen = $state(false);
	let busy = $state(false);

	let inPool = $derived(pool?.cards.filter((card) => card.in_pool).length ?? 0);

	// Nelle mappe "Sezioni" va sempre da solo; negli eventi la riga propria è l'effetto.
	function ownLine(label: string): boolean {
		return kind === 'mappe' ? label === 'Sezioni' : label === 'Effetto';
	}

	function requestChange(change: PendingChange) {
		pending = change;
		actionError = null;
		confirmOpen = true;
	}

	function askMembership(card: BoardPoolCard) {
		requestChange({
			card,
			patch: { in_pool: !card.in_pool },
			title: card.in_pool ? 'Togliere la carta dal mazzo?' : 'Reinserire la carta nel mazzo?',
			message: card.in_pool
				? `La carta "${card.nome}" uscirà dalla pool del campionato e non verrà più estratta.`
				: `La carta "${card.nome}" tornerà disponibile per le prossime estrazioni.`,
			confirmLabel: card.in_pool ? 'Togli dal mazzo' : 'Reinserisci'
		});
	}

	function askBlock(card: BoardPoolCard) {
		requestChange({
			card,
			patch: { blocked: !card.blocked },
			title: card.blocked ? 'Sbloccare la carta?' : 'Bloccare la carta?',
			message: card.blocked
				? `La carta "${card.nome}" tornerà disponibile per le estrazioni.`
				: `La carta "${card.nome}" resterà nella pool ma non verrà più estratta finché non la sblocchi.`,
			confirmLabel: card.blocked ? 'Sblocca' : 'Blocca'
		});
	}

	async function confirmChange() {
		if (!pending || busy) return;
		busy = true;
		const change = pending;
		try {
			const updated = await updateBoardPoolCard(championshipId, kind, change.card.id, change.patch);
			if (pool) {
				pool = {
					...pool,
					cards: pool.cards.map((card) => (card.id === updated.id ? updated : card))
				};
			}
			actionError = null;
		} catch (e) {
			actionError = errorMessage(e);
		} finally {
			busy = false;
			pending = null;
			confirmOpen = false;
		}
	}

	onMount(async () => {
		try {
			pool = await fetchBoardPool(championshipId, kind);
		} catch (e) {
			error = errorMessage(e);
		}
	});
</script>

<div class="space-y-3">
	{#if onback}
		<Button size="sm" variant="outline" onclick={onback}>← Indietro</Button>
	{/if}
	{#if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{:else if !pool}
		<p class="text-muted-foreground">Caricamento…</p>
	{:else}
		{#if actionError}
			<p class="text-sm text-destructive" role="alert">{actionError}</p>
		{/if}
		<p class="text-sm text-muted-foreground">
			{pool.cards.length} carte, {inPool} ancora in pool. Le carte fuori pool sono già state usate in
			una gara.
		</p>
		{#if pool.cards.length === 0}
			<p class="text-sm text-muted-foreground">Nessuna carta nel catalogo.</p>
		{:else}
			<ul class="grid grid-cols-1 gap-4 md:grid-cols-2">
				{#each pool.cards as card (card.id)}
					<li
						class="flex flex-col gap-2 rounded-lg border border-white/10 bg-[#161a26] p-4"
						class:opacity-60={!card.in_pool}
						data-in-pool={card.in_pool}
						data-blocked={card.blocked}
					>
						<h3
							class="truncate font-racing text-lg font-bold tracking-wide text-white uppercase"
							title={card.nome}
						>
							{card.nome}
						</h3>
						<div class="relative w-full max-w-[358px]">
							<img
								src={boardPoolImageUrl(card.image)}
								alt={`Carta ${card.nome}`}
								loading="lazy"
								class="aspect-[560/360] w-full rounded object-cover"
								class:brightness-50={!card.in_pool}
							/>
							{#if !card.in_pool}
								<span
									class="absolute inset-0 flex items-center justify-center rounded bg-black/50 text-red-500"
									title="Fuori dalla pool"
									aria-label="Fuori dalla pool"
								>
									<RacingIcon name="deck_export" size="xl" />
								</span>
							{:else if card.blocked}
								<span
									class="absolute inset-0 flex items-center justify-center rounded"
									title="Carta bloccata"
									aria-label="Carta bloccata"
								>
									<RacingIcon name="lock_closed" size={96} class="text-black/50" />
								</span>
							{/if}
							<div class="absolute top-1 right-1 z-10 flex flex-col items-center gap-1">
								{#if card.in_pool && !card.blocked}
									<button
										type="button"
										class="rounded bg-black/70 p-1 text-red-400 hover:bg-black/90"
										title="Togli dal mazzo"
										aria-label="Togli dal mazzo"
										onclick={() => askMembership(card)}
									>
										<RacingIcon name="deck_export" size="md" />
									</button>
								{:else if !card.in_pool}
									<button
										type="button"
										class="rounded bg-black/70 p-1 text-green-400 hover:bg-black/90"
										title="Reinserisci nel mazzo"
										aria-label="Reinserisci nel mazzo"
										onclick={() => askMembership(card)}
									>
										<RacingIcon name="deck_import" size="md" />
									</button>
								{/if}
								{#if card.in_pool}
									<button
										type="button"
										class="rounded bg-black/70 p-1 hover:bg-black/90"
										class:text-amber-300={card.blocked}
										class:text-white={!card.blocked}
										title={card.blocked ? 'Sblocca carta' : 'Blocca carta'}
										aria-label={card.blocked ? 'Sblocca carta' : 'Blocca carta'}
										onclick={() => askBlock(card)}
									>
										<RacingIcon name={card.blocked ? 'lock_closed' : 'lock_open'} size="md" />
									</button>
								{/if}
							</div>
						</div>
						<dl class="flex flex-wrap gap-x-3 gap-y-0.5 text-xs">
							{#each card.fields as field (field.label)}
								<div class="flex gap-1" class:basis-full={ownLine(field.label)}>
									<dt class="shrink-0 font-semibold text-muted-foreground">{field.label}:</dt>
									<dd class="break-words whitespace-pre-line">{field.value}</dd>
								</div>
							{/each}
						</dl>
						{#if !card.in_pool}
							<p class="font-racing text-xs font-bold tracking-wider text-red-500 uppercase">
								Fuori dalla pool
							</p>
						{:else if card.blocked}
							<p class="font-racing text-xs font-bold tracking-wider text-amber-300 uppercase">
								Carta bloccata
							</p>
						{/if}
					</li>
				{/each}
			</ul>
		{/if}
	{/if}
</div>

{#if pending}
	<ConfirmDialog
		bind:open={confirmOpen}
		title={pending.title}
		message={pending.message}
		confirmLabel={pending.confirmLabel}
		onconfirm={confirmChange}
	/>
{/if}
