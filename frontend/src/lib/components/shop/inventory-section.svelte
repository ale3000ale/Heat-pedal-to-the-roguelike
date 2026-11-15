<script lang="ts">
	import type { Snippet } from 'svelte';

	// Sezione a scomparsa dell'inventario: parte chiusa e mostra il numero di carte nel titolo.
	let { title, count, children }: { title: string; count: number; children: Snippet } = $props();
</script>

<details class="group overflow-hidden rounded-xl border border-white/10 bg-[#141824]" open>
	<summary
		class="flex cursor-pointer items-center justify-between px-4 py-3 font-racing text-sm font-bold tracking-wider text-white uppercase transition-colors select-none hover:bg-white/5"
	>
		<div class="flex items-center gap-2">
			<span>{title}</span>
			<span
				class="rounded-full border border-primary/30 bg-primary/20 px-2 py-0.5 font-racing text-xs font-black text-primary"
			>
				{count}
			</span>
		</div>
		<span
			aria-hidden="true"
			class="text-xs text-muted-foreground transition-transform group-open:rotate-180">▼</span
		>
	</summary>
	<div class="px-4 pt-2 pb-4">
		{@render children()}
	</div>
</details>
