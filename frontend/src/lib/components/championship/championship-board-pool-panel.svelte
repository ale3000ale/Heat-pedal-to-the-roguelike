<script lang="ts">
	import { onMount } from 'svelte';
	import { errorMessage } from '$lib/admin/shop-admin-format';
	import {
		boardPoolImageUrl,
		fetchBoardPool,
		type BoardPool,
		type BoardPoolKind
	} from '$lib/championship/board-pool-api';
	import { Button } from '$lib/components/ui/button';
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

	let pool = $state<BoardPool | null>(null);
	let error = $state<string | null>(null);

	let inPool = $derived(pool?.cards.filter((card) => card.in_pool).length ?? 0);

	// Nelle mappe "Sezioni" va sempre da solo; negli eventi la riga propria è l'effetto.
	function ownLine(label: string): boolean {
		return kind === 'mappe' ? label === 'Sezioni' : label === 'Effetto';
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
									<RacingIcon name="deck_export" size={64} />
								</span>
							{/if}
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
						{/if}
					</li>
				{/each}
			</ul>
		{/if}
	{/if}
</div>
