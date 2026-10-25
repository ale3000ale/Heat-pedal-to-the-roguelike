<script lang="ts">
	import CardTile from '$lib/components/CardTile.svelte';
	import InventorySection from '$lib/components/inventory-section.svelte';
	import DraftReady from '$lib/components/draft-ready.svelte';
	import { Button } from '$lib/components/ui/button';
	import { draftDeckView } from '$lib/draft-deck-view';
	import { totalCopies } from '$lib/inventory-count';
	import type { DraftDeckSession } from '$lib/draft-deck-session';
	import type { DraftStore } from '$lib/stores/draft.svelte';

	let { store, decks }: { store: DraftStore; decks: DraftDeckSession } = $props();
	const sessionState = $derived(store.state);
	const compatible = $derived(decks.owner === store && decks.draftId === sessionState.snapshot?.id);
	const view = $derived(draftDeckView(sessionState, $decks.pilotId, $decks.data));
	const locked = $derived($decks.busy || store.busy || $decks.status === 'blocked');

	$effect(() => {
		const current = decks;
		return () => current.dispose();
	});
	$effect(() => {
		if (decks.owner === store) decks.sync();
	});
	// Un solo caricamento iniziale quando si entra con un proprio presente non tutto READY.
	$effect(() => {
		if (
			compatible &&
			view.visible &&
			!view.allOwnReady &&
			view.selected &&
			sessionState.status === 'idle' &&
			$decks.status === 'empty' &&
			$decks.pilotId === null
		) {
			void decks.select(view.selected.pilot_id);
		}
	});

	function choosePilot(pilotId: number): void {
		if (compatible) void decks.select(pilotId);
	}
	function move(path: string, toGame: boolean): void {
		if (compatible) void decks.move(path, toGame);
	}
	function ready(value: boolean): void {
		if (compatible && view.selected) void decks.setReady(view.selected.pilot_id, value);
	}
</script>

{#if view.visible && compatible}
	{#if view.allOwnReady && view.selected && sessionState.status !== 'blocked' && $decks.status !== 'blocked'}
		<DraftReady
			pilotName={view.selected.name}
			busy={locked || !view.canUnready}
			onnotready={() => ready(false)}
		/>
	{:else}
		<section
			aria-label="Preparazione mazzi draft"
			aria-busy={$decks.busy || store.busy}
			class="space-y-4"
		>
			{#if view.ownPilots.length === 0}
				<p role="status">Non hai piloti presenti da preparare. Attendi gli altri partecipanti.</p>
			{:else}
				<div class="flex flex-wrap gap-2" aria-label="I tuoi piloti presenti">
					{#each view.ownPilots as pilot (pilot.pilot_id)}
						<Button
							type="button"
							variant="outline"
							aria-pressed={view.selected?.pilot_id === pilot.pilot_id}
							disabled={store.busy || $decks.status === 'writing' || sessionState.status !== 'idle'}
							onclick={() => choosePilot(pilot.pilot_id)}
						>
							{pilot.name}{sessionState.snapshot?.ready.includes(pilot.pilot_id) ? ' — pronto' : ''}
						</Button>
					{/each}
				</div>
				{#if view.selected}
					<h3 class="font-semibold">Mazzo di {view.selected.name}</h3>
					{#if $decks.error}
						<p role="alert" class="text-sm text-destructive">{$decks.error}</p>
					{/if}
					{#if $decks.busy}
						<p role="status" class="text-sm">Operazione in corso…</p>
					{/if}
					{#if !view.current}
						<p class="text-sm">
							Il mazzo deve essere caricato o verificato prima di modificare carte o confermare
							pronto.
						</p>
					{/if}
					{#if sessionState.status === 'blocked'}
						<p class="text-sm">Rileggi prima la preparazione dal comando del contenitore.</p>
					{/if}
					<Button
						type="button"
						variant="outline"
						disabled={$decks.busy || store.busy || sessionState.status !== 'idle'}
						onclick={() => choosePilot(view.selected!.pilot_id)}>Rileggi mazzo</Button
					>
					{#if view.hasDeck}
						<p class="text-sm">
							Mazzo {view.count}/15{view.current ? '' : ' — dati precedenti, non modificabili'}
						</p>
						<InventorySection title="Inventario modifiche" count={totalCopies(view.inventory)}>
							<div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
								{#each view.inventory as card (card.path)}
									<CardTile
										{card}
										compact
										disabled={locked || !view.canAdd}
										onclick={() => move(card.path, true)}
									/>
								{/each}
							</div>
						</InventorySection>
						<InventorySection title="Mazzo da gioco" count={view.count ?? 0}>
							<div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
								{#each view.gameDeck as card (card.path)}
									<CardTile
										{card}
										compact
										disabled={locked || !view.canEdit}
										onclick={() => move(card.path, false)}
									/>
								{/each}
							</div>
						</InventorySection>
					{/if}
					<div class="flex justify-end">
						{#if view.selectedReady}
							<Button
								type="button"
								variant="outline"
								disabled={locked || !view.canUnready}
								onclick={() => ready(false)}>non Pronto</Button
							>
						{:else}
							<Button type="button" disabled={locked || !view.canReady} onclick={() => ready(true)}
								>Pronto</Button
							>
						{/if}
					</div>
					<p class="text-sm text-muted-foreground">
						{sessionState.snapshot?.first_race
							? 'Prima gara: non sono richieste esattamente 15 copie; resta il massimo di 15.'
							: 'Per pronto sono richieste esattamente 15 copie.'}
					</p>
				{/if}
			{/if}
		</section>
	{/if}
{:else if view.visible}
	<p role="alert">Contesto del mazzo non corrispondente alla preparazione.</p>
{/if}
