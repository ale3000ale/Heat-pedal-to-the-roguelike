<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import Modal from '$lib/components/modal.svelte';
	import type { Pilot } from '$lib/types';

	// Finestra per scegliere uno dei propri piloti: un clic su un nome la chiude e chiama
	// `onselect` con il pilota scelto.
	let {
		open = $bindable(false),
		title,
		pilots,
		onselect
	}: {
		open?: boolean;
		title: string;
		pilots: Pilot[];
		onselect: (pilot: Pilot) => void;
	} = $props();

	function select(pilot: Pilot) {
		open = false;
		onselect(pilot);
	}
</script>

<Modal bind:open {title}>
	<div class="flex flex-col gap-2">
		{#each pilots as p (p.id)}
			<Button variant="outline" class="justify-start" onclick={() => select(p)}>{p.name}</Button>
		{/each}
	</div>
</Modal>
