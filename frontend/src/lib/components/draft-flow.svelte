<script lang="ts">
	import { untrack } from 'svelte';
	import { readable } from 'svelte/store';
	import { Button } from '$lib/components/ui/button';
	import DraftModal from '$lib/components/draft-modal.svelte';
	import DraftStart from '$lib/components/draft-start.svelte';
	import DraftAttendance from '$lib/components/draft-attendance.svelte';
	import DraftOrder from '$lib/components/draft-order.svelte';
	import DraftPicking from '$lib/components/draft-picking.svelte';
	import DraftDecks from '$lib/components/draft-decks.svelte';
	import { createDraftFlowContext, draftFlowView } from '$lib/draft-flow';
	import type { DraftFlowContext } from '$lib/draft-flow';
	import type { DraftDeckState } from '$lib/draft-deck-session';
	import type { DraftStore } from '$lib/stores/draft.svelte';

	let { store }: { store: DraftStore } = $props();
	// Inizializzazione esplicita non tracciata: il contesto viene poi mantenuto per owner/ID.
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

	$effect(() => {
		const owner = store;
		return () => {
			untrack(() => {
				if (context?.owner === owner) context.dispose();
				owner.dispose();
			});
		};
	});

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

	/** Passaggio locale richiesto da DraftStart; non salva una transizione inesistente. */
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
			{#key active}
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
