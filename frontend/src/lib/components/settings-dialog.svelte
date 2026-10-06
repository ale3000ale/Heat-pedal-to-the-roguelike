<script lang="ts">
	import type { Snippet } from 'svelte';
	import Modal from '$lib/components/modal.svelte';

	let {
		open = $bindable(false),
		title,
		children
	}: { open?: boolean; title: string; children: Snippet } = $props();
</script>

<Modal bind:open {title}>
	{@render children()}
</Modal>
