<script lang="ts">
	import Modal from '$lib/components/modal.svelte';
	import type { ReviewIncongruity } from '$lib/review-counts-types';

	let { open = $bindable(false), issues }: { open?: boolean; issues: ReviewIncongruity[] } =
		$props();
</script>

<Modal bind:open title="Incongruenze nelle carte">
	<p class="mb-3 text-sm">
		La revisione non è stata confermata. La bozza è conservata: correggi i conteggi e riprova.
	</p>
	<ul class="space-y-3">
		{#each issues as issue, index (index)}
			<li class="rounded border p-3 text-sm">
				<h3 class="font-semibold">{issue.card_name}</h3>
				<p>{issue.reason}</p>
				<p class="text-muted-foreground">
					Pool attuale: {issue.pool_now} · Dopo la revisione: {issue.pool_after} · Massimo:
					{issue.pool_max ?? 'non noto'}
				</p>
			</li>
		{/each}
	</ul>
</Modal>
