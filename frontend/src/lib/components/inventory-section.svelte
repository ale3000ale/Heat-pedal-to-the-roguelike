<script lang="ts">
	import type { Snippet } from 'svelte';

	// Sezione a scomparsa dell'inventario: parte chiusa e mostra il numero di carte nel titolo.
	let { title, count, children }: { title: string; count: number; children: Snippet } = $props();
</script>

<details class="group rounded-lg border">
	<summary class="flex cursor-pointer items-center justify-between px-3 py-2 font-semibold">
		<span>{title} ({count})</span>
		<span aria-hidden="true" class="transition group-open:rotate-180">▾</span>
	</summary>
	<div class="px-3 pb-3">
		{@render children()}
	</div>
</details>
