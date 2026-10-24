<script lang="ts">
	import type { Snippet } from 'svelte';

	// Sezione a scomparsa dell'inventario: parte chiusa e mostra il numero di carte nel titolo.
	let { title, count, children }: { title: string; count: number; children: Snippet } = $props();
</script>

<details class="group rounded-xl border border-white/10 bg-[#141824] overflow-hidden" open>
	<summary class="flex cursor-pointer items-center justify-between px-4 py-3 font-racing font-bold uppercase tracking-wider text-sm text-white select-none hover:bg-white/5 transition-colors">
		<div class="flex items-center gap-2">
			<span>{title}</span>
			<span class="rounded-full bg-primary/20 border border-primary/30 px-2 py-0.5 text-xs font-racing font-black text-primary">
				{count}
			</span>
		</div>
		<span aria-hidden="true" class="text-xs text-muted-foreground transition-transform group-open:rotate-180">▼</span>
	</summary>
	<div class="px-4 pb-4 pt-2">
		{@render children()}
	</div>
</details>
