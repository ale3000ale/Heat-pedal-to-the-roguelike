<script lang="ts">
	import type { Snippet } from 'svelte';
	import { Button } from '$lib/components/ui/button';

	// Con `closeOnOutside` falso la finestra si chiude solo con la X: il clic fuori e il
	// tasto Esc non fanno nulla.
	let {
		open = $bindable(false),
		title,
		closeOnOutside = true,
		children
	}: {
		open?: boolean;
		title: string;
		closeOnOutside?: boolean;
		children: Snippet;
	} = $props();

	function dismiss() {
		if (closeOnOutside) open = false;
	}

	function onkeydown(event: KeyboardEvent) {
		if (open && event.key === 'Escape') dismiss();
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
			onclick={dismiss}
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
