<script lang="ts">
	import type { Snippet } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import { shouldCloseModal } from './modal-close';

	// Pannello laterale per la navigazione su schermi stretti.
	let {
		open = $bindable(false),
		title = 'Navigazione',
		children
	}: {
		open?: boolean;
		title?: string;
		children: Snippet;
	} = $props();

	function requestClose(source: 'button' | 'escape' | 'outside') {
		if (shouldCloseModal(source, true)) open = false;
	}

	function onkeydown(event: KeyboardEvent) {
		if (open && event.key === 'Escape') requestClose('escape');
	}
</script>

<svelte:window {onkeydown} />

{#if open}
	<div class="fixed inset-0 z-50 md:hidden">
		<button
			type="button"
			class="absolute inset-0 cursor-default bg-black/50"
			aria-label="Chiudi"
			tabindex={-1}
			onclick={() => requestClose('outside')}
		></button>
		<div
			id="nav-drawer"
			role="dialog"
			aria-modal="true"
			aria-label={title}
			class="absolute inset-y-0 left-0 flex w-72 max-w-[85vw] flex-col overflow-y-auto border-r border-white/10 bg-[#0d1017] p-4 shadow-2xl"
		>
			<div class="mb-3 flex items-center justify-between gap-3">
				<h2 class="font-racing text-lg font-bold tracking-wider text-white uppercase">{title}</h2>
				<Button
					size="sm"
					variant="outline"
					aria-label="Chiudi"
					onclick={() => requestClose('button')}
				>
					✕
				</Button>
			</div>
			{@render children()}
		</div>
	</div>
{/if}
