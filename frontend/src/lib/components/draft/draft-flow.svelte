<script lang="ts">
	import { onDestroy, untrack } from 'svelte';
	import { readable } from 'svelte/store';
	import { Button } from '$lib/components/ui/button';
	import DraftModal from '$lib/components/draft/draft-modal.svelte';
	import DraftStart from '$lib/components/draft/draft-start.svelte';
	import DraftAttendance from '$lib/components/draft/draft-attendance.svelte';
	import DraftOrder from '$lib/components/draft/draft-order.svelte';
	import DraftPicking from '$lib/components/draft/draft-picking.svelte';
	import DraftDecks from '$lib/components/draft/draft-decks.svelte';
	import { createDraftFlowContext, draftFlowView } from '$lib/draft/draft-flow';
	import type { DraftFlowContext } from '$lib/draft/draft-flow';
	import type { DraftDeckSession, DraftDeckState } from '$lib/draft/deck/draft-deck-session';
	import type { DraftStore } from '$lib/stores/draft.svelte';

	let {
		store,
		ondecks
	}: {
		store: DraftStore;
		ondecks?: (owner: DraftStore, decks: DraftDeckSession | null, busy: boolean) => void;
	} = $props();
	let context = $state.raw<DraftFlowContext | null>(untrack(() => createDraftFlowContext(store)));
	let attendance = $state.raw<{ owner: DraftStore; draftId: number } | null>(null);
	const emptyDeck = readable<DraftDeckState>({
		status: 'empty',
		pilotId: null,
		data: null,
		error: null,
		busy: false
	});
	const sessionState = $derived(store.state);
	const active = $derived(
		context?.owner === store && context.draftId === sessionState.snapshot?.id ? context : null
	);
	const deck = $derived(active?.decks ?? emptyDeck);
	const view = $derived(
		draftFlowView(sessionState, attendance?.owner === store ? attendance.draftId : null, $deck.busy)
	);

	// Comunica identita e busy, non copie di carte. Default assente per i vecchi chiamanti.
	$effect(() => {
		const owner = store;
		const coordinator = active?.decks ?? null;
		const busy = $deck.busy;
		const callback = ondecks;
		untrack(() => callback?.(owner, coordinator, busy));
		return () => untrack(() => callback?.(owner, null, false));
	});
	// Solo il contesto locale appartiene alla vista. Lo store resta del registro host.
	onDestroy(() => untrack(() => context?.dispose()));
	$effect(() => {
		const owner = store;
		const root = sessionState;
		const existing = untrack(() => context);
		if (!root.snapshot || root.status === 'finished' || root.status === 'disposed') {
			if (existing)
				untrack(() => {
					existing.dispose();
					context = null;
				});
			return;
		}
		if (existing?.owner === owner && existing.draftId === root.snapshot.id) return;
		untrack(() => {
			existing?.dispose();
			context = createDraftFlowContext(owner);
		});
	});

	/** Passaggio locale: non salva una transizione server inesistente. */
	function showAttendance(): void {
		store.syncContext();
		const root = store.state;
		if (
			view.busy ||
			root.status !== 'idle' ||
			root.snapshot?.phase !== 'attendance' ||
			!root.snapshot.can_manage
		)
			return;
		attendance = { owner: store, draftId: root.snapshot.id };
	}
	async function load(): Promise<void> {
		if (view.busy || store.blocked) return;
		await store.refresh();
	}
</script>

{#if view.visible}
	<DraftModal {store} externalBusy={$deck.busy}>
		{#if active}
			{#key active.draftId}
				{#if view.screen === 'start'}
					<DraftStart {store} ondraft={showAttendance} />
				{:else if view.screen === 'attendance'}
					<DraftAttendance {store} />
				{:else if view.screen === 'order'}
					<DraftOrder {store} />
				{:else if view.screen === 'picking'}
					<DraftPicking {store} />
				{:else if view.screen === 'decks'}
					<DraftDecks {store} decks={active.decks} />
				{/if}
			{/key}
		{:else}
			<div class="space-y-3" aria-busy={view.busy}>
				<p role="status">Preparazione non ancora disponibile.</p>
				<Button type="button" disabled={view.busy || store.blocked} onclick={load}
					>Carica preparazione</Button
				>
			</div>
		{/if}
	</DraftModal>
{/if}
