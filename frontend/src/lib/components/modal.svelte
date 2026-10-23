<script lang="ts">
	import type { Snippet } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import { shouldCloseModal, type ModalCloseSource } from '$lib/modal-close';

	// Con `closeOnOutside` falso la finestra si chiude solo con la X: il clic fuori e il
	// tasto Esc non fanno nulla. Con `blur` lo sfondo è sfocato; con `wide` la finestra è
	// più larga (serve all'apertura dei pacchetti); con `narrow` è stretta (serve al banner
	// della carta ottenuta). Senza queste opzioni nulla cambia.
	// Con onrequestclose la chiusura e' delegata: il chiamante modifica open solo
	// dopo l'eventuale conferma, senza perdere automaticamente una bozza pendente.
	let {
		open = $bindable(false),
		title,
		closeOnOutside = true,
		blur = false,
		wide = false,
		narrow = false,
		onrequestclose,
		children
	}: {
		open?: boolean;
		title: string;
		closeOnOutside?: boolean;
		blur?: boolean;
		wide?: boolean;
		narrow?: boolean;
		onrequestclose?: () => void;
		children: Snippet;
	} = $props();

	function requestClose(source: ModalCloseSource) {
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
			<div class="mb-3 flex items-center justify-between gap-3">
				<h2 class="text-lg font-semibold">{title}</h2>
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
