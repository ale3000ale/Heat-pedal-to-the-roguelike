<script lang="ts">
	import { tick } from 'svelte';
	import {
		CARD_HEIGHT,
		CARD_WIDTH,
		MAX_ZOOM,
		initialView,
		panView,
		sourceRect,
		zoomView,
		type CropView
	} from '$lib/cards/card-crop';

	// Editor di ritaglio: mostra l'immagine scelta nell'area 560x870 della carta, che si sposta
	// trascinando e si ingrandisce con lo zoom. Ogni modifica produce un WebP pronto da inviare.
	interface Props {
		file: File;
		blob?: Blob | null;
	}

	// `blob` è una prop bindable solo scritta qui e letta dal genitore: ESLint non lo vede.
	// eslint-disable-next-line no-useless-assignment
	let { file, blob = $bindable() }: Props = $props();

	let canvas = $state<HTMLCanvasElement>();
	let image = $state<ImageBitmap | null>(null);
	let view = $state<CropView | null>(null);
	let loadError = $state<string | null>(null);
	let dragging: { x: number; y: number } | null = null;

	// Azzera il ritaglio esportato quando cambia il file.
	function clearBlob() {
		blob = null;
	}

	// Legge il file scelto e prepara la vista iniziale centrata.
	$effect(() => {
		const current = file;
		let cancelled = false;
		image = null;
		view = null;
		clearBlob();
		loadError = null;
		createImageBitmap(current).then(
			async (bitmap) => {
				if (cancelled) {
					bitmap.close();
					return;
				}
				image = bitmap;
				view = initialView(bitmap.width, bitmap.height);
				await tick();
				exportBlob();
			},
			() => {
				if (!cancelled) loadError = "Impossibile leggere l'immagine";
			}
		);
		return () => {
			cancelled = true;
		};
	});

	// Ridisegna l'anteprima a ogni cambio di vista.
	$effect(() => {
		if (!canvas || !image || !view) return;
		const context = canvas.getContext('2d');
		if (!context) return;
		const rect = sourceRect(view, image.width, image.height);
		context.clearRect(0, 0, CARD_WIDTH, CARD_HEIGHT);
		context.drawImage(image, rect.sx, rect.sy, rect.sw, rect.sh, 0, 0, CARD_WIDTH, CARD_HEIGHT);
	});

	// Salva il ritaglio attuale come WebP. Si chiama a fine trascinamento e a fine zoom.
	function exportBlob() {
		canvas?.toBlob(
			(result) => {
				blob = result;
			},
			'image/webp',
			0.9
		);
	}

	function startDrag(e: PointerEvent & { currentTarget: HTMLButtonElement }) {
		e.currentTarget.setPointerCapture(e.pointerId);
		dragging = { x: e.clientX, y: e.clientY };
	}

	// Sposta l'immagine; i pixel dello schermo si convertono in pixel della carta.
	function drag(e: PointerEvent & { currentTarget: HTMLButtonElement }) {
		if (!dragging || !view || !image) return;
		const ratio = CARD_WIDTH / (canvas?.clientWidth ?? e.currentTarget.clientWidth);
		const dx = (e.clientX - dragging.x) * ratio;
		const dy = (e.clientY - dragging.y) * ratio;
		dragging = { x: e.clientX, y: e.clientY };
		view = panView(view, dx, dy, image.width, image.height);
	}

	function endDrag() {
		if (!dragging) return;
		dragging = null;
		exportBlob();
	}

	/**
	 * Sposta il ritaglio con le frecce del controllo nativo; Maiusc usa un passo fine.
	 * @param event Evento tastiera; gli altri tasti mantengono il comportamento nativo.
	 * @returns Attende il ridisegno prima di esportare il WebP, senza nuove regole di ritaglio.
	 */
	async function keyPan(event: KeyboardEvent): Promise<void> {
		if (!view || !image) return;
		const step = event.shiftKey ? 1 : 10;
		const directions: Record<string, readonly [number, number]> = {
			ArrowLeft: [-step, 0],
			ArrowRight: [step, 0],
			ArrowUp: [0, -step],
			ArrowDown: [0, step]
		};
		const delta = directions[event.key];
		if (!delta) return;
		event.preventDefault();
		view = panView(view, delta[0], delta[1], image.width, image.height);
		await tick();
		exportBlob();
	}

	function changeZoom(e: Event & { currentTarget: HTMLInputElement }) {
		if (!view || !image) return;
		view = zoomView(view, e.currentTarget.valueAsNumber, image.width, image.height);
	}
</script>

<div class="space-y-3">
	{#if loadError}
		<p class="text-sm text-destructive" role="alert">{loadError}</p>
	{:else}
		<button
			type="button"
			class="block w-full max-w-[280px] rounded-md p-0 text-left focus-visible:outline-2 focus-visible:outline-offset-2"
			aria-label="Editor ritaglio: usa le frecce per spostare e Invio o Spazio per applicare"
			disabled={!image || !view}
			onpointerdown={startDrag}
			onpointermove={drag}
			onpointerup={endDrag}
			onpointercancel={endDrag}
			onkeydown={keyPan}
			onclick={exportBlob}
		>
			<canvas
				bind:this={canvas}
				width={CARD_WIDTH}
				height={CARD_HEIGHT}
				aria-label="Anteprima del ritaglio della carta"
			></canvas>
		</button>
		{#if view && image}
			<label class="block space-y-1 text-sm">
				<span>Zoom</span>
				<input
					type="range"
					min={1}
					max={MAX_ZOOM}
					step={0.01}
					value={view.zoom}
					oninput={changeZoom}
					onchange={exportBlob}
				/>
			</label>
			<p class="text-sm text-muted-foreground">
				Trascina o usa le frecce per centrare la carta (Maiusc: spostamento fine). Invio o Spazio
				applicano il ritaglio.
			</p>
		{/if}
	{/if}
</div>

<style>
	canvas {
		display: block;
		width: 100%;
		max-width: 280px;
		aspect-ratio: 560 / 870;
		touch-action: none;
		cursor: grab;
		border: 1px solid var(--border);
		border-radius: 0.375rem;
	}
</style>
