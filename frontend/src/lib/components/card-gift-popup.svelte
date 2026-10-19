<script lang="ts">
	import type { CardGift } from '$lib/card-play-types';
	import Modal from '$lib/components/modal.svelte';

	// Popup "Hai ottenuto una carta sponsor". Si chiude solo con la X; alla chiusura
	// chiama `onclosed`, che segna le notifiche come viste.
	let {
		open = $bindable(false),
		gifts,
		onclosed
	}: {
		open?: boolean;
		gifts: CardGift[];
		onclosed: () => void | Promise<void>;
	} = $props();

	let wasOpen = false;

	// Rileva il passaggio da aperto a chiuso, qualunque sia il modo in cui è avvenuto.
	$effect(() => {
		if (open) {
			wasOpen = true;
		} else if (wasOpen) {
			wasOpen = false;
			void onclosed();
		}
	});
</script>

<Modal bind:open title="Hai ottenuto una carta sponsor" closeOnOutside={false} blur narrow>
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
