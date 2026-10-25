<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import {
		advanceDraftOrder, canEditDraftOrder, createDraftOrder, draftOrderChanged,
		draftOrderMatches, draftOrderRows, moveDraftOrder
	} from '$lib/draft-order';
	import type { DraftOrderDraft } from '$lib/draft-order';
	import type { DraftStore } from '$lib/stores/draft.svelte';

	type LocalOrder = { owner: DraftStore; order: DraftOrderDraft };
	let { store }: { store: DraftStore } = $props();
	let edited = $state.raw<LocalOrder | null>(null);
	let discard = $state.raw<LocalOrder | null>(null);
	let dragging = $state.raw<{
		owner: DraftStore; pointerId: number; pilotId: number; original: DraftOrderDraft;
	} | null>(null);
	let list = $state<HTMLOListElement>();
	let submitting = $state(false);
	let notice = $state<string | null>(null);
	const state = $derived(store.state);
	const baseline = $derived(createDraftOrder(state));
	const dirty = $derived(edited !== null && edited.owner === store && draftOrderChanged(edited.order));
	const local = $derived(dirty && edited ? edited.order : baseline);
	const rows = $derived(local ? draftOrderRows(local) : []);
	const stale = $derived(dirty && local !== null && !draftOrderMatches(state, local));
	const available = $derived(state.snapshot?.phase === 'order' && state.status !== 'finished' && state.status !== 'disposed');
	const editable = $derived(local !== null && !submitting && discard === null && canEditDraftOrder(state, local));

	function move(pilotId: number, index: number): void {
		store.syncContext();
		if (!editable || !local) return;
		edited = { owner: store, order: moveDraftOrder(local, pilotId, index) };
		notice = 'Ordine modificato localmente. Avanti lo conferma sul server.';
	}

	function beginDrag(event: PointerEvent, pilotId: number): void {
		store.syncContext();
		if (!editable || !local || dragging || event.button !== 0 || !event.isPrimary) return;
		const handle = event.currentTarget;
		if (!(handle instanceof HTMLButtonElement)) return;
		handle.setPointerCapture(event.pointerId);
		dragging = { owner: store, pointerId: event.pointerId, pilotId, original: local };
		event.preventDefault();
	}

	function drag(event: PointerEvent): void {
		const captured = dragging;
		if (!captured || captured.owner !== store || captured.pointerId !== event.pointerId || !editable || !local) return;
		const row = document.elementFromPoint(event.clientX, event.clientY)?.closest<HTMLElement>('[data-order-pilot]');
		if (!row || !list?.contains(row)) return;
		const index = local.pilotIds.indexOf(Number(row.dataset.orderPilot));
		if (index >= 0 && index !== local.pilotIds.indexOf(captured.pilotId)) move(captured.pilotId, index);
	}

	function endDrag(event: PointerEvent): void {
		if (dragging?.pointerId === event.pointerId) dragging = null;
	}

	function cancelDrag(event: PointerEvent): void {
		const captured = dragging;
		if (!captured || captured.pointerId !== event.pointerId) return;
		if (captured.owner === store) edited = { owner: store, order: captured.original };
		dragging = null;
	}

	/** Scarta solo la bozza esplicitamente confermata; non rilegge e non libera blocchi server. */
	function discardLocal(): void {
		if (submitting || store.busy) return;
		if (discard && discard === edited && discard.owner === store) edited = null;
		discard = null;
		notice = 'Bozza locale scartata. Restano validi eventuali blocchi del server.';
	}

	/** Un solo flusso esplicito: order se necessario, poi start dopo rilettura dello snapshot in memoria. */
	async function next(): Promise<void> {
		store.syncContext();
		if (!editable || !local || dragging) return;
		const target = store;
		const captured = edited;
		const order = local;
		submitting = true;
		notice = null;
		try {
			const result = await advanceDraftOrder(order, {
				state: () => target.state,
				save: (pilotIds) => target.command('order', { pilot_ids: pilotIds }),
				start: () => target.command('start', {})
			});
			if (store !== target) return;
			if (result.accepted && edited === captured) edited = null;
			if (!result.started) {
				notice = result.accepted
					? 'Ordine presente sul server, ma avvio non confermato. Nessun nuovo tentativo automatico.'
					: 'Ordine non confermato: verifica errore o variazioni dello stato prima di procedere.';
			}
		} finally {
			submitting = false;
		}
	}
</script>

{#if available}
	<section aria-label="Ordine draft" aria-busy={submitting || store.busy} class="space-y-4">
		{#if state.snapshot?.first_race}
			<strong class="block text-center">Prima gara</strong>
		{/if}
		<p class="text-sm text-muted-foreground">
			Ordine ricevuto dal server. Il creatore puo trascinare i nomi oppure usare Su e Giu.
		</p>
		{#if stale}
			<p role="alert" class="text-sm text-destructive">
				Lo stato server e cambiato. La bozza e conservata, ma non puo essere inviata.
			</p>
		{/if}
		{#if !local}
			<p role="alert" class="text-sm text-destructive">Ordine non utilizzabile: verifica lo stato server.</p>
		{/if}
		{#if notice}
			<p role="status" class="text-sm">{notice}</p>
		{/if}
		<ol bind:this={list} aria-label="Ordine di scelta" class="space-y-2" inert={discard !== null}>
			{#each rows as pilot, index (pilot.pilot_id)}
				<li data-order-pilot={pilot.pilot_id} class="flex flex-wrap items-center gap-2 rounded-md border p-3">
					<span class="min-w-0 flex-1 break-words">{index + 1}. {pilot.name}</span>
					<button
						type="button"
						class="touch-none rounded-md border px-3 py-2"
						disabled={!editable}
						aria-label={`Trascina ${pilot.name}`}
						onpointerdown={(event) => beginDrag(event, pilot.pilot_id)}
						onpointermove={drag}
						onpointerup={endDrag}
						onpointercancel={cancelDrag}
						onlostpointercapture={cancelDrag}
					>↕</button>
					<Button type="button" size="sm" variant="outline" disabled={!editable || index === 0 || dragging !== null}
						aria-label={`Sposta su ${pilot.name}`} onclick={() => move(pilot.pilot_id, index - 1)}>Su</Button>
					<Button type="button" size="sm" variant="outline" disabled={!editable || index === rows.length - 1 || dragging !== null}
						aria-label={`Sposta giu ${pilot.name}`} onclick={() => move(pilot.pilot_id, index + 1)}>Giu</Button>
				</li>
			{/each}
		</ol>
		{#if dirty}
			<Button type="button" variant="outline" disabled={submitting || store.busy || dragging !== null}
				onclick={() => (discard = edited)}>Scarta ordine locale</Button>
		{/if}
		{#if discard}
			<div class="space-y-2 rounded-md border p-3">
				<p class="text-sm">Scartare le modifiche locali all ordine?</p>
				<div class="flex flex-wrap gap-2">
					<Button type="button" variant="outline" disabled={submitting || store.busy} onclick={() => (discard = null)}>Conserva bozza</Button>
					<Button type="button" variant="destructive" disabled={submitting || store.busy} onclick={discardLocal}>Scarta bozza</Button>
				</div>
			</div>
		{/if}
		<div class="flex justify-end">
			<Button type="button" disabled={!editable || dragging !== null} onclick={next}>Avanti</Button>
		</div>
	</section>
{/if}
