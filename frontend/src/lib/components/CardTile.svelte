<script lang="ts">
	import type { CardEntry } from '$lib/types';

	let { card }: { card: CardEntry } = $props();
</script>

<figure class="relative overflow-hidden rounded-lg border bg-card">
	<img
		src="/media/{card.path}"
		alt={card.name}
		loading="lazy"
		class="aspect-[2/3] w-full object-cover"
	/>
	<figcaption class="flex items-center justify-between gap-2 px-2 py-1.5 text-sm">
		<span class="truncate font-medium">{card.name}</span>
		<span
			class="rounded-full bg-primary px-2 py-0.5 text-xs font-semibold text-primary-foreground"
			title="Copie possedute"
		>
			×{card.copies}
		</span>
	</figcaption>
</figure>
