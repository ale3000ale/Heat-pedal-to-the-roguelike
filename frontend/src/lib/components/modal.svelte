<script lang="ts">
	import type { Snippet } from 'svelte';
	import { Button } from '$lib/components/ui/button';

	let {
		open = $bindable(false),
		title,
		children
	}: { open?: boolean; title: string; children: Snippet } = $props();

	function onkeydown(event: KeyboardEvent) {
		if (open && event.key === 'Escape') open = false;
	}
</script>

<svelte:window {onkeydown} />

{#if open}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4">
		<button
			type="button"
			class="absolute inset-0 cursor-default bg-black/50"
			aria-label="Chiudi"
			tabindex={-1}
			onclick={() => (open = false)}
		></button>
		<div
			role="dialog"
			aria-modal="true"
			aria-label={title}
			class="relative max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-lg border bg-background p-4 text-foreground shadow-lg"
		>
			<div class="mb-3 flex items-center justify-between gap-3">
				<h2 class="text-lg font-semibold">{title}</h2>
				<Button size="sm" variant="outline" aria-label="Chiudi" onclick={() => (open = false)}>
					✕
				</Button>
			</div>
			{@render children()}
		</div>
	</div>
{/if}
