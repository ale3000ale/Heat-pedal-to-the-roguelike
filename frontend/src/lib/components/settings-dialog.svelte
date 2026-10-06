<script lang="ts">
	import type { Snippet } from 'svelte';
	import { Button } from '$lib/components/ui/button';

	let {
		open = $bindable(false),
		title,
		children
	}: { open?: boolean; title: string; children: Snippet } = $props();

	let dialog = $state<HTMLDialogElement>();

	$effect(() => {
		if (!dialog) return;
		if (open && !dialog.open) dialog.showModal();
		else if (!open && dialog.open) dialog.close();
	});
</script>

<dialog
	bind:this={dialog}
	class="m-auto w-full max-w-lg rounded-lg border bg-background p-4 text-foreground backdrop:bg-black/50"
	aria-label={title}
	onclose={() => (open = false)}
>
	<div class="mb-3 flex items-center justify-between gap-3">
		<h2 class="text-lg font-semibold">{title}</h2>
		<Button size="sm" variant="outline" aria-label="Chiudi" onclick={() => (open = false)}>
			✕
		</Button>
	</div>
	{#if open}
		{@render children()}
	{/if}
</dialog>
