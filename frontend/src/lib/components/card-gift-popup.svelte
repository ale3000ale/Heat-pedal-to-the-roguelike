<script lang="ts">
	import type { CardGift } from '$lib/card-play-types';
	import Modal from '$lib/components/modal.svelte';

	let {
		open = $bindable(false),
		gifts,
		onclosed
	}: {
		open?: boolean;
		gifts: CardGift[];
		onclosed: (shown: CardGift[]) => void | Promise<void>;
	} = $props();

	let renderedGifts: CardGift[] = [];

	// Gli effetti Svelte vengono eseguiti dopo l'aggiornamento del DOM. Il click deve
	// usare l'ultima lista resa, non nuove notifiche assegnate prima del prossimo render.
	$effect(() => {
		if (open) renderedGifts = [...gifts];
	});

	function getOpen(): boolean {
		return open;
	}

	/**
	 * Riceve soltanto le variazioni originate dal Modal, non quelle del genitore.
	 * @param next Nuovo stato del Modal; con closeOnOutside=false si chiude con la X.
	 * @returns Nessun valore. Il chiamante gestisce gli errori della callback asincrona.
	 * Una chiusura remota o di lifecycle del genitore non richiama onclosed.
	 */
	function setOpen(next: boolean): void {
		if (open && !next) {
			const shown = [...renderedGifts];
			open = false;
			void onclosed(shown);
		} else {
			open = next;
		}
	}
</script>

<Modal
	bind:open={getOpen, setOpen}
	title="Hai ottenuto una carta sponsor"
	closeOnOutside={false}
	blur
	narrow
>
	<ul class="flex flex-wrap justify-center gap-3">
		{#each gifts as gift (gift.id)}
			<li class="w-48 overflow-hidden rounded-lg border bg-card">
				<img
					src="/media/{gift.card_path}"
					alt={gift.card_name}
					class="aspect-[2/3] w-full object-cover"
				/>
				<p class="px-2 py-1.5 text-center text-sm font-medium">{gift.card_name}</p>
			</li>
		{/each}
	</ul>
</Modal>
