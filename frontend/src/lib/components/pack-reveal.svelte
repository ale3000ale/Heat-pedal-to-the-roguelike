<script lang="ts">
	import { onMount, untrack } from 'svelte';
	import { fly } from 'svelte/transition';
	import CardTile from '$lib/components/CardTile.svelte';
	import { Button } from '$lib/components/ui/button';
	import {
		PHASE_DURATIONS_MS,
		cardDelayMs,
		initialPhase,
		nextPhase,
		type RevealPhase
	} from '$lib/pack-reveal-phases';
	import type { RevealedCard } from '$lib/shop-cards';

	// Apertura in quattro fasi: busta chiusa (con l'immagine del pacchetto come texture),
	// strappo della striscia in alto, scorrimento della busta verso il basso, carte in fila
	// che entrano da sinistra. Ogni carta si gira da sola al tocco; `done` diventa vero
	// quando sono tutte girate. Il componente nasce a ogni apertura, quindi riparte da zero.
	let {
		cards,
		packImage = null,
		done = $bindable(false)
	}: { cards: RevealedCard[]; packImage?: string | null; done?: boolean } = $props();

	let phase = $state<RevealPhase>('sealed');
	let flipped = $state<boolean[]>(untrack(() => cards.map(() => false)));
	let remaining = $derived(flipped.filter((value) => !value).length);
	let textureStyle = $derived(packImage ? `background-image: url('${packImage}')` : '');

	// Con il movimento ridotto si salta busta e animazioni.
	onMount(() => {
		phase = initialPhase(window.matchMedia('(prefers-reduced-motion: reduce)').matches);
	});

	// Strappo e scorrimento avanzano da soli dopo la loro durata.
	$effect(() => {
		if (phase !== 'tearing' && phase !== 'sliding') return;
		const timer = setTimeout(() => (phase = nextPhase(phase)), PHASE_DURATIONS_MS[phase]);
		return () => clearTimeout(timer);
	});

	// Aggiorna `done` solo quando cambia, così l'effetto non si ripete.
	$effect(() => {
		const finished = remaining === 0;
		if (done !== finished) done = finished;
	});

	function openPack() {
		if (phase === 'sealed') phase = nextPhase(phase);
	}

	function flip(index: number) {
		flipped[index] = true;
	}

	// Durante la busta salta le animazioni; con le carte in fila le gira tutte.
	function skip() {
		if (phase !== 'cards') {
			phase = 'cards';
			return;
		}
		flipped = flipped.map(() => true);
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
	{:else}
		<div class="row">
			{#each cards as item, index (index)}
				<div class="cell" in:fly={{ x: -80, duration: 400, delay: cardDelayMs(index) }}>
					<div class="flip" class:is-flipped={flipped[index]}>
						<button
							type="button"
							onclick={() => flip(index)}
							disabled={flipped[index]}
							aria-label={`Gira la carta ${index + 1}`}
							class="face back"
						>
							?
						</button>
						<div class="face front">
							<CardTile card={item.card} title="Copie ottenute" />
						</div>
					</div>
					<p class="mt-1 min-h-4 text-xs text-muted-foreground">
						{#if flipped[index]}
							{item.section === 'modifiche' ? 'Modifica' : 'Sponsor'}
						{/if}
					</p>
				</div>
			{/each}
		</div>
	{/if}

	{#if remaining > 0}
		<div class="flex flex-wrap items-center justify-between gap-3">
			<p class="text-sm text-muted-foreground">Carte da girare: {remaining}</p>
			<Button size="sm" variant="outline" onclick={skip}>Salta</Button>
		</div>
	{:else if cards.length > 0}
		<p class="text-sm text-muted-foreground">Hai girato tutte le carte.</p>
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

	.pack {
		position: relative;
		width: min(60vw, 240px);
		aspect-ratio: 560 / 870;
		border-radius: 0.75rem;
		box-shadow: 0 12px 28px rgb(0 0 0 / 0.35);
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

	.row {
		display: flex;
		gap: 0.75rem;
		overflow-x: auto;
		padding: 0.5rem 0.25rem;
		perspective: 900px;
	}

	.cell {
		flex: 0 0 8rem;
	}

	.flip {
		position: relative;
		aspect-ratio: 2 / 3;
		transform-style: preserve-3d;
		transition: transform 600ms ease;
	}

	.flip.is-flipped {
		transform: rotateY(180deg);
	}

	.face {
		position: absolute;
		inset: 0;
		backface-visibility: hidden;
		-webkit-backface-visibility: hidden;
	}

	.back {
		display: flex;
		align-items: center;
		justify-content: center;
		border: 2px dashed var(--border);
		border-radius: 0.5rem;
		background: var(--muted);
		font-size: 1.5rem;
		font-weight: 700;
	}

	.back:not(:disabled):hover {
		outline: 2px solid var(--primary);
	}

	.front {
		transform: rotateY(180deg);
	}

	@media (prefers-reduced-motion: reduce) {
		.pack,
		.pack-strip,
		.flip {
			transition: none;
		}
	}
</style>
