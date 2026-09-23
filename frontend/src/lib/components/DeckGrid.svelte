<!-- frontend/src/lib/components/DeckGrid.svelte -->
<!-- Griglia di carte per un mazzo/prototipo: mostra immagine (path relativo) e valore di ogni carta. -->
<script lang="ts">
	export let cards: { path: string; value: number }[];

	// cardName(path)
	// path: percorso relativo dell'immagine carta (es. "src/images/cards/3_SpeedBoost.png").
	// Estrae un nome leggibile dal filename N_nome.ext per mostrarlo come etichetta sotto l'immagine.
	function cardName(path: string): string {
		const filename = path.split('/').pop() ?? path;
		const withoutExt = filename.replace(/\.[^/.]+$/, '');
		const parts = withoutExt.split('_');
		return parts.slice(1).join(' ') || withoutExt;
	}
</script>

<div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
	{#each cards as card}
		<div class="app-card text-center">
			<img
				src={`/${card.path}`}
				alt={cardName(card.path)}
				class="w-full aspect-[2/3] object-cover rounded-lg mb-2 bg-racing-silver/20"
				loading="lazy"
			/>
			<p class="font-semibold text-sm">{cardName(card.path)}</p>
			<p class="text-xs opacity-70">Valore: {card.value}</p>
		</div>
	{/each}

	{#if cards.length === 0}
		<p class="text-sm opacity-70 col-span-full">Nessuna carta disponibile.</p>
	{/if}
</div>
