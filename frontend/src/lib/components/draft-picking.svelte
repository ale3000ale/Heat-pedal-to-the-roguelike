<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import DraftPickingCard from '$lib/components/draft-picking-card.svelte';
	import {
		canConfirmDraftChoice,
		draftPickingView,
		proposeDraftChoice,
		proposeDraftPreview
	} from '$lib/draft-picking';
	import type { DraftChoiceProposal } from '$lib/draft-picking';
	import type { DraftStore } from '$lib/stores/draft.svelte';

	let { store }: { store: DraftStore } = $props();
	let selection = $state.raw<{ owner: DraftStore; proposal: DraftChoiceProposal } | null>(null);
	let submitting = $state(false);
	let notice = $state<string | null>(null);
	const sessionState = $derived(store.state);
	const view = $derived(draftPickingView(sessionState));
	const canConfirm = $derived(
		selection !== null &&
			selection.owner === store &&
			canConfirmDraftChoice(sessionState, selection.proposal)
	);

	function enlarged(slotId: number): boolean {
		return store.zoomedSlotId === slotId;
	}

	$effect(() => {
		if (selection && !submitting && !canConfirm) {
			selection = null;
			notice =
				'La scelta e cambiata o non e piu il tuo turno: verifica la copia prima di confermare.';
		}
	});

	/** Zoom locale nello store. Solo il proprietario di turno puo aggiornare preview. */
	async function zoom(slotId: number): Promise<void> {
		if (selection || submitting || store.busy) return;
		store.syncContext();
		const current = store.state;
		const picking = draftPickingView(current);
		const slot = current.snapshot?.cards.find((item) => item.slot_id === slotId);
		if (!picking.visible || !picking.coherent || !picking.turn || !current.snapshot || !slot)
			return;
		const closing = store.zoomedSlotId === slotId;
		if (!store.toggleZoom(slotId)) return;
		const sharedSlot = !closing && slot.chosen_by === null ? slotId : null;
		const payload = proposeDraftPreview(current, sharedSlot);
		if (payload && current.snapshot.preview_slot_id !== sharedSlot) {
			await store.command('preview', payload);
		}
	}

	function requestChoice(slotId: number): void {
		if (selection || submitting || store.busy) return;
		store.syncContext();
		if (!enlarged(slotId)) return;
		const proposal = proposeDraftChoice(store.state, slotId);
		if (!proposal) return;
		notice = null;
		selection = { owner: store, proposal };
	}

	/** Ricontrolla lo stesso store, turno, versione e slot senza aggiornamenti ottimistici. */
	async function confirmChoice(): Promise<void> {
		if (submitting) return;
		const captured = selection;
		store.syncContext();
		if (
			!captured ||
			captured.owner !== store ||
			!canConfirmDraftChoice(store.state, captured.proposal)
		) {
			selection = null;
			notice = 'Conferma non piu valida. Rileggi lo stato se necessario.';
			return;
		}
		const target = store;
		submitting = true;
		try {
			const completed = await target.command('choice', { slot_id: captured.proposal.slotId });
			if (!completed && store === target)
				notice = 'Scelta non confermata. Nessun reinvio automatico.';
		} finally {
			if (selection === captured) selection = null;
			submitting = false;
		}
	}
</script>

{#if view.visible}
	<section
		aria-label="Scelta carte draft"
		aria-busy={submitting || store.busy}
		class={view.ownedTurn
			? 'space-y-5 rounded-xl bg-emerald-900 p-4 text-white'
			: 'space-y-5 rounded-xl bg-red-950 p-4 text-white'}
	>
		{#if view.coherent && view.turn}
			{#if view.ownedTurn}
				<p role="status" class="turn-pulse text-center text-xl font-bold">tocca a te</p>
			{:else}
				<p role="status" class="text-center text-xl font-bold">Tocca a {view.turn.name}</p>
			{/if}
		{:else}
			<p role="alert">
				Stato del turno non utilizzabile. Verifica i dati server prima di proseguire.
			</p>
		{/if}
		{#if notice}
			<p role="status" class="text-sm">{notice}</p>
		{/if}
		{#if selection}
			<div class="space-y-3 rounded-md border border-white/40 p-3" aria-busy={submitting}>
				<p>Scegliere {selection.proposal.cardName} per {selection.proposal.pilotName}?</p>
				<div class="flex flex-wrap justify-end gap-2">
					<Button
						type="button"
						variant="outline"
						disabled={submitting}
						onclick={() => (selection = null)}>Torna alle carte</Button
					>
					<Button type="button" disabled={submitting || !canConfirm} onclick={confirmChoice}>
						{submitting ? 'Scelta in corso…' : 'Conferma scelta'}
					</Button>
				</div>
			</div>
		{/if}
		{#if view.coherent}
			<div class="space-y-5" inert={selection !== null || submitting}>
				<section aria-label="Copie disponibili" class="space-y-3">
					<h3 class="font-semibold">Carte disponibili</h3>
					<div class="flex flex-wrap items-start gap-4">
						{#each view.availableCards as slot (slot.slot_id)}
							<DraftPickingCard
								{slot}
								enlarged={enlarged(slot.slot_id)}
								previewPilotName={view.previewSlotId === slot.slot_id
									? (view.turn?.name ?? null)
									: null}
								chooseAllowed={view.canChoose && !submitting && selection === null}
								disabled={store.busy || submitting || selection !== null}
								onzoom={() => {
									void zoom(slot.slot_id);
								}}
								onchoose={() => requestChoice(slot.slot_id)}
							/>
						{/each}
					</div>
				</section>
				<section aria-label="Copie scelte" class="space-y-3">
					<h3 class="font-semibold">Carte scelte</h3>
					{#if view.pickedCards.length === 0}
						<p class="text-sm">Nessuna carta scelta.</p>
					{:else}
						<div class="flex flex-wrap items-start gap-4">
							{#each view.pickedCards as picked (picked.slot.slot_id)}
								<DraftPickingCard
									slot={picked.slot}
									enlarged={enlarged(picked.slot.slot_id)}
									pickedBy={picked.pilot.name}
									disabled={store.busy || submitting || selection !== null}
									onzoom={() => {
										void zoom(picked.slot.slot_id);
									}}
								/>
							{/each}
						</div>
					{/if}
				</section>
			</div>
		{/if}
	</section>
{/if}

<style>
	.turn-pulse {
		animation: draft-turn-pulse 1.2s ease-in-out infinite;
	}
	@keyframes draft-turn-pulse {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.4;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.turn-pulse {
			animation: none;
		}
	}
</style>
