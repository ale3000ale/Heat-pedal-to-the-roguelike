<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import Modal from '$lib/components/modal.svelte';

	let {
		open = $bindable(false),
		title,
		message,
		confirmLabel,
		cancelLabel = 'Annulla',
		onconfirm
	}: {
		open?: boolean;
		title: string;
		message: string;
		confirmLabel: string;
		cancelLabel?: string;
		onconfirm: () => void | Promise<void>;
	} = $props();

	async function confirm() {
		open = false;
		await onconfirm();
	}
</script>

<Modal bind:open {title}>
	<p class="text-sm text-muted-foreground">{message}</p>
	<div class="mt-4 flex justify-end gap-2">
		<Button variant="outline" onclick={() => (open = false)}>{cancelLabel}</Button>
		<Button variant="destructive" onclick={confirm}>{confirmLabel}</Button>
	</div>
</Modal>
