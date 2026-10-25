<script lang="ts">
	import type { Snippet } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import { shouldCloseModal, type ModalCloseSource } from '$lib/modal-close';

	// I valori predefiniti conservano il comportamento dei modal esistenti.
	// closeOnOutside controlla Escape/sfondo; showClose e closeDisabled solo la X.
	// onrequestclose delega la chiusura senza cambiare automaticamente open.
	let {
		open = $bindable(false),
		title,
		closeOnOutside = true,
		blur = false,
		wide = false,
		narrow = false,
		showClose = true,
		closeDisabled = false,
		closePosition = 'right',
		onrequestclose,
		children
	}: {
		open?: boolean;
		title: string;
		closeOnOutside?: boolean;
		blur?: boolean;
		wide?: boolean;
		narrow?: boolean;
		showClose?: boolean;
		closeDisabled?: boolean;
		closePosition?: 'left' | 'right';
		onrequestclose?: () => void;
		children: Snippet;
	} = $props();

	function requestClose(source: ModalCloseSource) {
		if (source === 'button' && (!showClose || closeDisabled)) return;
		if (shouldCloseModal(source, closeOnOutside, onrequestclose)) open = false;
	}

	function onkeydown(event: KeyboardEvent) {
		if (open && event.key === 'Escape') requestClose('escape');
	}
</script>

<svelte:window {onkeydown} />

{#if open}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4">
		<button
			type="button"
			class={`absolute inset-0 cursor-default ${blur ? 'bg-black/60 backdrop-blur-sm' : 'bg-black/50'}`}
			aria-label="Chiudi"
			tabindex={-1}
			onclick={() => requestClose('outside')}
		></button>
		<div
			role="dialog"
			aria-modal="true"
			aria-label={title}
			class={`relative max-h-[90vh] w-full ${wide ? 'max-w-3xl' : narrow ? 'max-w-xs' : 'max-w-lg'} overflow-y-auto rounded-lg border bg-background p-4 text-foreground shadow-lg`}
		>
			<div
				class={`mb-3 flex items-center justify-between gap-3 ${closePosition === 'left' ? 'flex-row-reverse' : ''}`}
			>
				<h2 class="text-lg font-semibold">{title}</h2>
				{#if showClose}
					<Button
						size="sm"
						variant="outline"
						aria-label="Chiudi"
						disabled={closeDisabled}
						onclick={() => requestClose('button')}
					>
						✕
					</Button>
				{/if}
			</div>
			{@render children()}
		</div>
	</div>
{/if}
