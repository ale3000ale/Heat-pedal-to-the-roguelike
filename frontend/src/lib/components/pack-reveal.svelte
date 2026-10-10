<script lang="ts">
	import { onMount } from 'svelte';
	import { fly } from 'svelte/transition';
	import CardTile from '$lib/components/CardTile.svelte';
	import { Button } from '$lib/components/ui/button';
	import {
		PHASE_DURATIONS_MS,
		initialPhase,
		nextPhase,
		type RevealPhase
	} from '$lib/pack-reveal-phases';
	import type { RevealedCard } from '$lib/shop-cards';

	// Apertura in quattro fasi: busta chiusa (con l'immagine del pacchetto come texture),
	// strappo della striscia in alto (la striscia se ne va e la busta resta tagliata),
	// scorrimento della busta verso il basso, poi le carte UNA ALLA VOLTA: la prima compare
	// al centro e ogni tocco la fa scorrere verso sinistra mostrando la seguente.
	// `done` diventa vero quando e' visibile l'ultima carta.
	// Il componente nasce a ogni apertura, quindi riparte da zero.
	let {
		cards,
		packImage = null,
		done = $bindable(false)
	}: { cards: RevealedCard[]; packImage?: string | null; done?: boolean } = $props();

	let phase = $state<RevealPhase>('sealed');
	let current = $state(0);
	let reduced = $state(false);
	let lastIndex = $derived(Math.max(cards.length - 1, 0));
	let item = $derived(cards[current]);
	let textureStyle = $derived(packImage ? `background-image: url('${packImage}')` : '');
	let slideMs = $derived(reduced ? 0 : 350);

	// Con il movimento ridotto si salta busta e animazioni.
	onMount(() => {
		reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
		phase = initialPhase(reduced);
	});

	// Strappo e scorrimento avanzano da soli dopo la loro durata.
	$effect(() => {
		if (phase !== 'tearing' && phase !== 'sliding') return;
		const timer = setTimeout(() => (phase = nextPhase(phase)), PHASE_DURATIONS_MS[phase]);
		return () => clearTimeout(timer);
	});

	// Aggiorna `done` solo quando cambia, così l'effetto non si ripete.
	$effect(() => {
		const finished = cards.length === 0 || current >= lastIndex;
		if (done !== finished) done = finished;
	});

	function openPack() {
		if (phase === 'sealed') phase = nextPhase(phase);
	}

	// Passa alla carta seguente; sull'ultima non fa nulla.
	function nextCard() {
		if (current < lastIndex) current += 1;
	}

	function onCardKey(event: KeyboardEvent) {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			nextCard();
		}
	}

	// Durante la busta salta le animazioni; con le carte va direttamente all'ultima.
	function skip() {
		if (phase !== 'cards') {
			phase = 'cards';
			return;
		}
		current = lastIndex;
	}
</script>

<div class="space-y-4">
	{#if cards.length === 0}
		<p class="text-sm text-muted-foreground">Nessuna carta.</p>
	{/if}

	{#if phase !== 'cards'}
		<div class="stage">
			<button
				type="button"
				class="pack"
				class:sliding={phase === 'sliding'}
				class:tearing={phase === 'tearing'}
				onclick={openPack}
				disabled={phase !== 'sealed'}
				aria-label="Apri il pacchetto"
			>
				<span class="pack-body" style={textureStyle}></span>
				<span class="pack-strip" style={textureStyle}></span>
			</button>
			{#if phase === 'sealed'}
				<p class="text-center text-sm text-muted-foreground">Tocca la busta per aprirla.</p>
			{/if}
		</div>
	{:else if item}
		<div class="viewer">
			{#key current}
				<div
					class="slot"
					in:fly={{ x: 160, duration: slideMs }}
					out:fly={{ x: -160, duration: slideMs }}
				>
					<div
						class="current"
						role="button"
						tabindex={current < lastIndex ? 0 : -1}
						aria-label={current < lastIndex
							? `Carta ${current + 1} di ${cards.length}: tocca per la successiva`
							: `Ultima carta, ${current + 1} di ${cards.length}`}
						onclick={nextCard}
						onkeydown={onCardKey}
					>
						<CardTile card={item.card} title="Copie ottenute" />
					</div>
					<p class="mt-2 text-center text-xs text-muted-foreground">
						{item.section === 'modifiche' ? 'Modifica' : 'Sponsor'}
					</p>
				</div>
			{/key}
		</div>
	{/if}

	{#if cards.length > 0 && phase === 'cards'}
		<div class="flex flex-wrap items-center justify-between gap-3">
			{#if current < lastIndex}
				<p class="text-sm text-muted-foreground">
					Carta {current + 1} di {cards.length}: tocca per la successiva.
				</p>
				<Button size="sm" variant="outline" onclick={skip}>Salta</Button>
			{:else}
				<p class="text-sm text-muted-foreground">Ultima carta ({cards.length} di {cards.length}).</p>
			{/if}
		</div>
	{:else if phase !== 'cards'}
		<div class="flex justify-end">
			<Button size="sm" variant="outline" onclick={skip}>Salta</Button>
		</div>
	{/if}
</div>

<style>
	.stage {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.75rem;
		overflow: hidden;
		padding: 0.5rem 0;
	}

	/* L'ombra segue la forma reale della busta (anche tagliata), non il rettangolo. */
	.pack {
		position: relative;
		width: min(60vw, 240px);
		aspect-ratio: 560 / 870;
		border-radius: 0.75rem;
		filter: drop-shadow(0 10px 12px rgb(0 0 0 / 0.35));
		transition:
			transform 600ms ease-in,
			opacity 600ms ease-in;
	}

	.pack:not(:disabled):hover {
		transform: scale(1.03);
	}

	.pack.sliding {
		transform: translateY(130%);
		opacity: 0;
	}

	.pack-body,
	.pack-strip {
		position: absolute;
		left: 0;
		right: 0;
		background-color: var(--muted);
		background-repeat: no-repeat;
	}

	.pack-body {
		top: 0;
		bottom: 0;
		border-radius: 0.75rem;
		background-size: cover;
		background-position: center;
	}

	/* Dopo lo strappo la parte alta della busta (14%) viene tagliata via, con un bordo
	   leggermente irregolare: sotto resta solo il resto del pacchetto. Il taglio è
	   immediato perché la striscia, che lo copriva, parte nello stesso istante. */
	.pack.tearing .pack-body,
	.pack.sliding .pack-body {
		clip-path: polygon(
			0% 14.5%,
			8% 15.7%,
			17% 14.2%,
			26% 15.5%,
			35% 14.3%,
			44% 15.8%,
			53% 14.4%,
			62% 15.6%,
			71% 14.2%,
			80% 15.7%,
			89% 14.4%,
			100% 15.5%,
			100% 100%,
			0% 100%
		);
	}

	/* La striscia in alto riusa la stessa texture, allineata alla parte alta della busta. */
	.pack-strip {
		top: 0;
		height: 14%;
		border-radius: 0.75rem 0.75rem 0 0;
		background-size: 100% 714.29%;
		background-position: top;
		border-bottom: 2px dashed rgb(255 255 255 / 0.7);
		transform-origin: left bottom;
		transition:
			transform 700ms ease-out,
			opacity 700ms ease-out;
	}

	.pack.tearing .pack-strip,
	.pack.sliding .pack-strip {
		transform: translate(25%, -160%) rotate(-14deg);
		opacity: 0;
	}

	/* Una sola carta alla volta: entrante e uscente occupano la stessa cella della griglia,
	   così durante lo scorrimento si sovrappongono invece di impilarsi. */
	.viewer {
		display: grid;
		justify-items: center;
		overflow: hidden;
		padding: 0.5rem 0;
	}

	.slot {
		grid-area: 1 / 1;
		width: min(60vw, 240px);
	}

	.current {
		cursor: pointer;
		border-radius: 0.5rem;
	}

	.current:focus-visible {
		outline: 2px solid var(--primary);
		outline-offset: 2px;
	}
</style>
