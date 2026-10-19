<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import ReviewPilotInventory from '$lib/components/review-pilot-inventory.svelte';
	import ReviewIncongruenceDialog from '$lib/components/review-incongruence-dialog.svelte';
	import { ReviewCountsStore } from '$lib/stores/review-counts.svelte';
	import { formatCountdown } from '$lib/race-review-format';

	let {
		championshipId,
		raceId,
		autoOpen = false,
		canOpen = false,
		reopen = false
	}: {
		championshipId: number;
		raceId: number;
		autoOpen?: boolean;
		canOpen?: boolean;
		reopen?: boolean;
	} = $props();

	// svelte-ignore state_referenced_locally
	const store = new ReviewCountsStore(championshipId, raceId);
	onMount(() => {
		if (autoOpen) void store.start();
	});
	onDestroy(() => store.dispose());

	// La pagina della gara carica lo stato in onMount. Dopo una transizione riuscita
	// la ricarichiamo per aggiornare anche intestazione e permessi, non solo il pannello.
	async function transition(action: () => Promise<boolean>) {
		if (await action()) window.location.reload();
	}
</script>

<Card.Root>
	<Card.Header>
		<Card.Title>Revisione degli inventari sponsor</Card.Title>
		<Card.Description>
			Controlla le copie rimaste rispetto al totale avuto, inclusi i bonus S. + ripristina una
			copia; − ne conferma il consumo. Prossimo salva la bozza e spunta il pilota.
		</Card.Description>
	</Card.Header>
	<Card.Content class="space-y-4">
		{#if store.active}
			<p class="text-sm" role="timer" aria-live="off">
				Tempo rimasto: {formatCountdown(store.remaining)}
			</p>
			<p class="text-xs text-muted-foreground">
				Alla scadenza il server applica le carte coerenti dell'ultima bozza salvata e lascia
				invariate quelle incongruenti.
			</p>
			<div class="space-y-3">
				{#each store.pilots as pilot, index (pilot.pilot_id)}
					<section class="rounded-lg border p-3">
						<button
							type="button"
							class="flex w-full items-center justify-between gap-2 text-left font-medium"
							aria-expanded={store.index === index}
							disabled={store.busy}
							onclick={() => store.navigate(store.index === index ? -1 : index)}
						>
							<span>{pilot.pilot_name}</span>
							<span>
								{store.checked.includes(pilot.pilot_id) ? '✓ Controllato' : 'Da controllare'} ·
								{store.index === index ? '−' : '+'}
							</span>
						</button>
						{#if store.index === index}
							<div class="mt-3 space-y-3">
								<ReviewPilotInventory
									{pilot}
									disabled={store.busy || !store.active}
									onadjust={(name, delta) => store.adjust(pilot.pilot_id, name, delta)}
								/>
								<div class="flex flex-wrap justify-between gap-2">
									<Button
										type="button"
										variant="outline"
										disabled={store.busy || index === 0}
										onclick={() => store.navigate(index - 1)}>Indietro</Button
									>
									<Button
										type="button"
										disabled={store.busy}
										onclick={() =>
											store.navigate(index + 1 < store.pilots.length ? index + 1 : -1, true)}
									>
										{index + 1 < store.pilots.length ? 'Prossimo' : 'Completa controllo'}
									</Button>
								</div>
							</div>
						{/if}
					</section>
				{/each}
			</div>
			<div class="flex flex-wrap gap-2">
				<Button
					type="button"
					disabled={store.busy || !store.allReviewed}
					onclick={() => transition(() => store.confirm())}>Conferma revisione</Button
				>
				<Button
					type="button"
					variant="outline"
					disabled={store.busy}
					onclick={() => transition(() => store.abandon())}>Salva e rinuncia</Button
				>
			</div>
			<p class="text-sm text-muted-foreground">
				{store.checked.length}/{store.pilots.length} piloti controllati. La conferma richiede tutte le
				spunte.
			</p>
		{:else if store.review?.review_closed_at}
			<p class="text-sm text-green-600">Revisione conclusa.</p>
			{#if canOpen}
				<Button
					type="button"
					disabled={store.busy}
					onclick={() => transition(() => store.start(true))}>Riapri la revisione</Button
				>
			{/if}
		{:else if canOpen}
			<Button
				type="button"
				disabled={store.busy}
				onclick={() => transition(() => store.start(reopen))}
			>
				{reopen ? 'Riapri la revisione' : 'Apri la revisione'}
			</Button>
		{/if}
		{#if store.error}
			<p class="text-sm text-destructive" role="alert">{store.error}</p>
		{/if}
		{#if store.notice}
			<p class="text-sm text-muted-foreground" role="status">{store.notice}</p>
		{/if}
		{#if !store.active && store.review && !store.review.review_closed_at}
			<Button
				type="button"
				variant="outline"
				disabled={store.busy}
				onclick={() => transition(() => store.refreshStatus())}>Aggiorna stato</Button
			>
		{/if}
	</Card.Content>
</Card.Root>

<ReviewIncongruenceDialog bind:open={store.conflictOpen} issues={store.issues} />
