<script lang="ts">
	import { Button } from '$lib/components/ui/button';

	let {
		pilotName,
		busy = false,
		onnotready
	}: {
		pilotName: string;
		busy?: boolean;
		onnotready: () => void;
	} = $props();
</script>

<section
	aria-label="Tutti i tuoi piloti pronti"
	aria-busy={busy}
	class="relative flex min-h-72 flex-col items-center justify-center gap-6 overflow-hidden rounded-xl bg-black/85 p-6 text-white"
>
	<p role="status" class="sr-only">Tutti i tuoi piloti presenti sono pronti.</p>
	<span aria-hidden="true" class="ready-mark text-6xl font-black sm:text-8xl">READY</span>
	<p class="text-center text-sm">Per tornare alla modifica: {pilotName}</p>
	<Button type="button" variant="outline" disabled={busy} onclick={onnotready}>non Pronto</Button>
</section>

<style>
	.ready-mark {
		background: repeating-conic-gradient(#fff 0% 25%, #252525 0% 50%) 0 0 / 16px 16px;
		background-clip: text;
		-webkit-background-clip: text;
		color: transparent;
		-webkit-text-stroke: 2px white;
		transform: rotate(-12deg);
		animation: draft-ready-pulse 1.6s ease-in-out infinite alternate;
	}
	@keyframes draft-ready-pulse {
		from {
			transform: rotate(-12deg) scale(0.95);
		}
		to {
			transform: rotate(-12deg) scale(1.05);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.ready-mark {
			animation: none;
		}
	}
</style>
