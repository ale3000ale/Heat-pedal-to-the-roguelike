<script lang="ts">
	import type { Snippet } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import { shouldCloseModal, type ModalCloseSource } from '$lib/components/shared/modal-close';

	// I valori predefiniti conservano il comportamento dei modal esistenti.
	// closeOnOutside controlla Escape/sfondo; showClose e closeDisabled solo la X.
	// onrequestclose delega la chiusura senza cambiare automaticamente open.
	// stableViewport e opt-in: non ricentra il riquadro a ogni variazione del contenuto.
	// fitContent e opt-in: altezza pari al contenuto, ancorata in alto per non saltare.
	let {
		open = $bindable(false),
		title,
		closeOnOutside = true,
		blur = false,
		wide = false,
		narrow = false,
		stableViewport = false,
		fitContent = false,
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
		stableViewport?: boolean;
		fitContent?: boolean;
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
	<div
		class={`fixed inset-0 z-50 flex justify-center ${fitContent ? 'items-start p-2 sm:p-6' : 'items-center p-4'}`}
	>
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
			class={`relative max-h-[90vh] w-full ${wide ? 'max-w-3xl' : narrow ? 'max-w-xs' : 'max-w-lg'} overflow-y-auto rounded-lg border bg-background ${fitContent ? 'p-3 sm:p-4' : 'p-4'} text-foreground shadow-lg`}
			class:viewport-stable={stableViewport}
			class:viewport-fit={fitContent}
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

<style>
	/* Altezza indipendente dal contenuto; vh e il fallback per browser senza dvh. */
	.viewport-stable {
		box-sizing: border-box;
		height: 90vh;
		height: 90dvh;
		max-height: calc(100vh - 2rem);
		max-height: calc(100dvh - 2rem);
		scrollbar-gutter: stable;
	}
	/* Si adatta al contenuto fino allo spazio disponibile, anche su telefono. */
	.viewport-fit {
		box-sizing: border-box;
		max-height: calc(100vh - 1rem);
		max-height: calc(100dvh - 1rem);
		overscroll-behavior: contain;
		scrollbar-gutter: stable;
	}
	@media (min-width: 640px) {
		.viewport-fit {
			max-height: calc(100vh - 3rem);
			max-height: calc(100dvh - 3rem);
		}
	}
</style>
