<script lang="ts">
	import { tick } from 'svelte';
	import CardTile from '$lib/components/CardTile.svelte';
	import InventorySection from '$lib/components/inventory-section.svelte';
	import DraftReady from '$lib/components/draft-ready.svelte';
	import { Button } from '$lib/components/ui/button';
	import { captureDraftDeckScroll } from '$lib/draft-deck-scroll';
	import { draftDeckView } from '$lib/draft-deck-view';
	import { totalCopies } from '$lib/inventory-count';
	import type { DraftDeckSession } from '$lib/draft-deck-session';
	import type { DraftStore } from '$lib/stores/draft.svelte';

	let { store, decks }: { store: DraftStore; decks: DraftDeckSession } = $props();
	let inventoryGrid = $state<HTMLDivElement>();
	let gameGrid = $state<HTMLDivElement>();
	let pendingScroll: {
		coordinator: DraftDeckSession['subscribe'];
		handle: ReturnType<typeof captureDraftDeckScroll>;
	} | null = null;
	const sessionState = $derived(store.state);
	const compatible = $derived(decks.owner === store && decks.draftId === sessionState.snapshot?.id);
	const view = $derived(draftDeckView(sessionState, $decks.pilotId, $decks.data));
	const locked = $derived($decks.busy || store.busy || $decks.status === 'blocked');
	const coordinatorIdentity = $derived(decks.subscribe);

	// La vista possiede solo la cattura scroll, non il coordinatore del contesto.
	$effect(() => {
		const identity = coordinatorIdentity;
		return () => {
			if (pendingScroll?.coordinator === identity) {
				pendingScroll.handle?.cancel();
				pendingScroll = null;
			}
		};
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

	/** Sposta una copia con il coordinatore esistente e aggiorna solo lo scroll UI.
	 * path identifica la carta; toGame sceglie la griglia di origine. Nessun reinvio.
	 * Attende POST e GET del coordinatore, poi tick; recupera solo dopo successo e
	 * nello stesso store/coordinatore/pilota aggiornato. Il finally pulisce anche
	 * su errore; lo smontaggio cancella subito i listener della cattura pendente.
	 */
	async function move(path: string, toGame: boolean): Promise<void> {
		if (!compatible || locked || !view.selected) return;
		const owner = store;
		const target = decks;
		const pilotId = view.selected.pilot_id;
		pendingScroll?.handle?.cancel();
		const captured = {
			// La factory crea subscribe una volta per coordinatore, non per emissione.
			coordinator: target.subscribe,
			handle: captureDraftDeckScroll(toGame ? inventoryGrid : gameGrid)
		};
		pendingScroll = captured;
		try {
			const completed = await target.move(path, toGame);
			if (!completed) return;
			await tick();
			if (
				pendingScroll === captured &&
				store === owner &&
				decks.subscribe === captured.coordinator &&
				compatible &&
				view.visible &&
				view.selected?.pilot_id === pilotId &&
				view.current &&
				!locked
			)
				captured.handle?.restore();
		} finally {
			captured.handle?.cancel();
			if (pendingScroll === captured) pendingScroll = null;
		}
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
				{#if view.ownPilots.length > 1}
					<div class="flex flex-wrap gap-2" aria-label="I tuoi piloti presenti">
						{#each view.ownPilots as pilot (pilot.pilot_id)}
							<Button
								type="button"
								variant="outline"
								aria-pressed={view.selected?.pilot_id === pilot.pilot_id}
								disabled={store.busy ||
									$decks.status === 'writing' ||
									sessionState.status !== 'idle'}
								onclick={() => choosePilot(pilot.pilot_id)}
							>
								{pilot.name}{sessionState.snapshot?.ready.includes(pilot.pilot_id)
									? ' — pronto'
									: ''}
							</Button>
						{/each}
					</div>
				{/if}
				{#if view.selected}
					<h3
						class="rounded-lg border border-amber-400/50 bg-amber-500/20 px-4 py-3 text-center font-racing text-xl font-black tracking-wider text-amber-300 uppercase"
					>
						Mazzo di {view.selected.name}{#if view.hasDeck}: {view.count}/15{view.current
								? ''
								: ' — dati precedenti, non modificabili'}{/if}
					</h3>
					{#if view.hasDeck}
						<InventorySection title="Mazzo da gioco" count={view.count ?? 0}>
							<div bind:this={gameGrid} class="grid grid-cols-2 gap-3 sm:grid-cols-4">
								{#each view.gameDeck as card (card.path)}
									<CardTile
										{card}
										compact
										hoverZoom={false}
										hoverFocus
										disabled={locked || !view.canEdit}
										onclick={() => {
											void move(card.path, false);
										}}
									/>
								{/each}
							</div>
						</InventorySection>
						<InventorySection title="Inventario modifiche" count={totalCopies(view.inventory)}>
							<div bind:this={inventoryGrid} class="grid grid-cols-2 gap-3 sm:grid-cols-4">
								{#each view.inventory as card (card.path)}
									<CardTile
										{card}
										compact
										hoverZoom={false}
										hoverFocus
										disabled={locked || !view.canAdd}
										onclick={() => {
											void move(card.path, true);
										}}
									/>
								{/each}
							</div>
						</InventorySection>
					{/if}
					{#if $decks.error}
						<p role="alert" class="text-sm text-destructive">{$decks.error}</p>
					{/if}
					<!-- Conserva le righe e il loro wrapping anche quando non sono pertinenti. -->
					<div class="space-y-1" data-draft-deck-feedback>
						<p
							role="status"
							class="text-sm"
							class:invisible={!$decks.busy}
							aria-hidden={!$decks.busy}
							data-draft-deck-busy
						>
							Operazione in corso…
						</p>
						<p
							class="text-sm"
							class:invisible={view.current}
							aria-hidden={view.current}
							data-draft-deck-verification
						>
							Il mazzo deve essere caricato o verificato prima di modificare carte o confermare
							pronto.
						</p>
					</div>
					{#if sessionState.status === 'blocked'}
						<p class="text-sm">Rileggi prima la preparazione dal comando del contenitore.</p>
					{/if}
					<div class="-mt-2 flex justify-end">
						{#if view.selectedReady}
							<Button
								type="button"
								variant="outline"
								disabled={locked || !view.canUnready}
								size="lg"
								onclick={() => ready(false)}>non Pronto</Button
							>
						{:else}
							<Button
								type="button"
								size="lg"
								disabled={locked || !view.canReady}
								onclick={() => ready(true)}>Pronto</Button
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
