<script lang="ts">
	import { onDestroy } from 'svelte';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import PilotPlaysList from '$lib/components/pilot-plays-list.svelte';
	import CardAdjustForm from '$lib/components/card-adjust-form.svelte';
	import { RaceReviewStore } from '$lib/stores/race-review.svelte';
	import { formatCountdown } from '$lib/race-review-format';

	// Pannello di revisione delle carte per giudice e admin, su una gara terminata.
	let { championshipId, raceId }: { championshipId: number; raceId: number } = $props();

	// Lo store è legato a una gara: la pagina rimonta il pannello se la gara cambia.
	// svelte-ignore state_referenced_locally
	const store = new RaceReviewStore(championshipId, raceId);

	onDestroy(() => store.stopTimer());
</script>

<Card.Root>
	<Card.Header>
		<Card.Title>Revisione delle carte</Card.Title>
		<Card.Description>
			Apri la revisione per annullare giocate, dare o togliere carte. Hai 15 minuti: poi la
			revisione scade e può riprenderla un altro giudice. Alla conferma le carte giocate vengono
			consumate.
		</Card.Description>
	</Card.Header>
	<Card.Content class="space-y-4">
		<div class="flex flex-wrap items-center gap-3">
			{#if store.active}
				<span class="text-sm font-medium" role="timer" aria-live="off">
					Tempo rimasto: {formatCountdown(store.remaining)}
				</span>
				<Button type="button" disabled={store.busy} onclick={() => store.confirm()}>
					Conferma revisione
				</Button>
				<Button
					type="button"
					variant="outline"
					disabled={store.busy}
					onclick={() => store.abandon()}
				>
					Rinuncia
				</Button>
			{:else if store.confirmed}
				<span class="text-sm font-medium text-green-600">Revisione confermata.</span>
			{:else}
				<Button type="button" disabled={store.busy} onclick={() => store.open()}>
					{store.review ? 'Riapri la revisione' : 'Apri la revisione'}
				</Button>
				{#if store.review && !store.review.in_review}
					<span class="text-sm text-muted-foreground">Revisione chiusa o scaduta.</span>
				{/if}
			{/if}
		</div>

		{#if store.error}
			<p class="text-sm text-destructive" role="alert">{store.error}</p>
		{/if}
		{#if store.notice}
			<p class="text-sm text-muted-foreground" role="status">{store.notice}</p>
		{/if}

		{#if store.review}
			<div class="space-y-4">
				{#each store.pilots as pilot (pilot.pilot_id)}
					<PilotPlaysList
						{pilot}
						canCancel={store.active}
						busy={store.busy}
						onCancel={(playId) => store.cancel(playId)}
					/>
				{:else}
					<p class="text-sm text-muted-foreground">Nessun pilota da mostrare.</p>
				{/each}
			</div>

			{#if store.active}
				<CardAdjustForm
					pilots={store.pilots}
					busy={store.busy}
					onBonus={(id, name) => store.bonus(id, name)}
					onRemove={(id, name) => store.remove(id, name)}
				/>
			{/if}
		{/if}
	</Card.Content>
</Card.Root>
