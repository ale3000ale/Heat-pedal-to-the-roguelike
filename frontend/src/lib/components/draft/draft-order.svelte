<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import {
		advanceDraftOrder,
		canEditDraftOrder,
		createDraftOrder,
		draftOrderChanged,
		draftOrderMatches,
		draftOrderRows,
		moveDraftOrder
	} from '$lib/draft/order/draft-order';
	import { flip } from 'svelte/animate';
	import { onDestroy } from 'svelte';
	import {
		orderAutoScrollStep,
		orderDragClamp,
		orderDragOffset,
		orderDragRow,
		orderDragTarget
	} from '$lib/draft/order/draft-order-drag';
	import type { DraftOrderDraft } from '$lib/draft/order/draft-order';
	import type { DraftStore } from '$lib/stores/draft.svelte';

	type LocalOrder = { owner: DraftStore; order: DraftOrderDraft };
	let { store }: { store: DraftStore } = $props();
	let edited = $state.raw<LocalOrder | null>(null);
	let discard = $state.raw<LocalOrder | null>(null);
	let dragging = $state.raw<{
		owner: DraftStore;
		pointerId: number;
		pilotId: number;
		original: DraftOrderDraft;
		container: HTMLOListElement;
		centers: number[];
		minDelta: number;
		maxDelta: number;
		from: number;
		startY: number;
		scroller: HTMLElement | null;
		scrollStart: number;
	} | null>(null);
	/** Traslazione visiva della scheda trascinata; non entra nella bozza. */
	let dragOffset = $state(0);
	let lastClientY = 0;
	let scrollFrame: number | null = null;
	let list = $state<HTMLOListElement>();
	let submitting = $state(false);
	let notice = $state<string | null>(null);
	const sessionState = $derived(store.state);
	const baseline = $derived(createDraftOrder(sessionState));
	const dirty = $derived(
		edited !== null && edited.owner === store && draftOrderChanged(edited.order)
	);
	const local = $derived(dirty && edited ? edited.order : baseline);
	const rows = $derived(local ? draftOrderRows(local) : []);
	const stale = $derived(dirty && local !== null && !draftOrderMatches(sessionState, local));
	const available = $derived(
		sessionState.snapshot?.phase === 'order' &&
			sessionState.status !== 'finished' &&
			sessionState.status !== 'disposed'
	);
	const editable = $derived(
		local !== null && !submitting && discard === null && canEditDraftOrder(sessionState, local)
	);

	function move(pilotId: number, index: number): void {
		store.syncContext();
		if (!editable || !local) return;
		edited = { owner: store, order: moveDraftOrder(local, pilotId, index) };
		notice = 'Ordine modificato localmente. Avanti lo conferma sul server.';
	}

	/** Cattura sulla lista stabile, non sulla scheda che viene riposizionata nel DOM. */
	function beginDrag(event: PointerEvent, pilotId: number): void {
		store.syncContext();
		const container = list;
		if (!editable || !local || !container || dragging || event.button !== 0 || !event.isPrimary)
			return;
		const elements = [...container.querySelectorAll<HTMLElement>('[data-order-pilot]')];
		if (
			elements.length !== local.pilotIds.length ||
			elements.some(
				(element, index) => Number(element.dataset.orderPilot) !== local.pilotIds[index]
			)
		)
			return;
		const from = local.pilotIds.indexOf(pilotId);
		if (from < 0) return;
		const centers = elements.map((element) => {
			const rect = element.getBoundingClientRect();
			return (rect.top + rect.bottom) / 2;
		});
		orderDragTarget(centers, from, 0);
		const bounds = container.getBoundingClientRect();
		const card = elements[from].getBoundingClientRect();
		const scroller = container.closest<HTMLElement>('[role="dialog"]');
		container.setPointerCapture(event.pointerId);
		dragging = {
			owner: store,
			pointerId: event.pointerId,
			pilotId,
			original: local,
			container,
			centers,
			minDelta: orderDragClamp(-Infinity, bounds, card),
			maxDelta: orderDragClamp(Infinity, bounds, card),
			from,
			startY: event.clientY,
			scroller,
			scrollStart: scroller?.scrollTop ?? 0
		};
		dragOffset = 0;
		lastClientY = event.clientY;
		scrollFrame = requestAnimationFrame(autoScroll);
		event.preventDefault();
	}

	/** Riposiziona bozza e scheda dalla stessa geometria iniziale, per puntatore o scroll. */
	function follow(clientY: number): void {
		const captured = dragging;
		if (!captured || captured.owner !== store) return;
		store.syncContext();
		if (!editable || !local) return;
		const scrollDelta = (captured.scroller?.scrollTop ?? 0) - captured.scrollStart;
		// Il limite vale anche per lo scroll automatico: la scheda non esce dalla lista.
		const deltaY = Math.min(
			captured.maxDelta,
			Math.max(captured.minDelta, clientY - captured.startY + scrollDelta)
		);
		const index = orderDragTarget(captured.centers, captured.from, deltaY);
		if (index !== local.pilotIds.indexOf(captured.pilotId)) move(captured.pilotId, index);
		dragOffset = orderDragOffset(captured.centers, captured.from, index, deltaY);
	}

	function drag(event: PointerEvent): void {
		const captured = dragging;
		if (!captured || captured.owner !== store || captured.pointerId !== event.pointerId) return;
		lastClientY = event.clientY;
		follow(event.clientY);
		event.preventDefault();
	}

	/** Scorre il dialog vicino ai bordi anche con puntatore fermo. */
	function autoScroll(): void {
		scrollFrame = null;
		const captured = dragging;
		if (!captured) return;
		const scroller = captured.scroller;
		if (scroller) {
			const rect = scroller.getBoundingClientRect();
			const step = orderAutoScrollStep(lastClientY, rect.top, rect.bottom);
			const before = scroller.scrollTop;
			if (step !== 0) scroller.scrollTop = before + step;
			if (scroller.scrollTop !== before) follow(lastClientY);
		}
		scrollFrame = requestAnimationFrame(autoScroll);
	}

	function stopAutoScroll(): void {
		if (scrollFrame !== null) cancelAnimationFrame(scrollFrame);
		scrollFrame = null;
	}

	onDestroy(stopAutoScroll);

	/** Azzera il gesto prima di release: lostpointercapture non deve annullare un drop riuscito. */
	function finishDrag(event: PointerEvent, cancelled: boolean): void {
		const captured = dragging;
		if (!captured || captured.pointerId !== event.pointerId) return;
		stopAutoScroll();
		dragging = null;
		dragOffset = 0;
		if (cancelled && captured.owner === store) edited = { owner: store, order: captured.original };
		if (captured.container.hasPointerCapture(captured.pointerId))
			captured.container.releasePointerCapture(captured.pointerId);
	}
	function endDrag(event: PointerEvent): void {
		finishDrag(event, false);
	}
	function cancelDrag(event: PointerEvent): void {
		finishDrag(event, true);
	}

	/** Scarta solo la bozza confermata, senza rete o sblocco dello stato server. */
	function discardLocal(): void {
		if (submitting || store.busy) return;
		if (discard && discard === edited && discard.owner === store) edited = null;
		discard = null;
		notice = 'Bozza locale scartata. Restano validi eventuali blocchi del server.';
	}

	/** Salva order se modificato e poi start: due HTTP, nessun rollback o retry inventato. */
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
			if (!result.started)
				notice = result.accepted
					? 'Ordine presente sul server, ma avvio non confermato. Nessun nuovo tentativo automatico.'
					: 'Ordine non confermato: verifica errore o variazioni dello stato prima di procedere.';
		} finally {
			submitting = false;
		}
	}
</script>

{#if available}
	<section aria-label="Ordine draft" aria-busy={submitting || store.busy} class="space-y-4">
		{#if sessionState.snapshot?.first_race}<strong class="block text-center">Prima gara</strong
			>{/if}
		<p class="text-sm text-muted-foreground">
			Ordine ricevuto dal server. Trascina l'intera scheda del pilota oppure usa le frecce.
		</p>
		{#if stale}<p role="alert" class="text-sm text-destructive">
				Lo stato server e cambiato. La bozza e conservata, ma non puo essere inviata.
			</p>{/if}
		{#if !local}<p role="alert" class="text-sm text-destructive">
				Ordine non utilizzabile: verifica lo stato server.
			</p>{/if}
		<p role="status" class="min-h-5 text-sm">{notice ?? ''}</p>
		<ol
			bind:this={list}
			aria-label="Ordine di scelta"
			class="space-y-2"
			inert={discard !== null}
			onpointermove={drag}
			onpointerup={endDrag}
			onpointercancel={cancelDrag}
			onlostpointercapture={cancelDrag}
		>
			{#each rows as pilot, index (pilot.pilot_id)}
				{@const lifted = dragging?.pilotId === pilot.pilot_id}
				<li
					animate:flip={{ duration: lifted ? 0 : 160 }}
					data-order-pilot={pilot.pilot_id}
					data-order-draggable={editable ? 'true' : 'false'}
					use:orderDragRow={{ pilotId: pilot.pilot_id, start: beginDrag }}
					title={editable ? 'Trascina la scheda per cambiare ordine' : undefined}
					style:transform={lifted ? `translateY(${dragOffset}px)` : undefined}
					class="order-row relative flex flex-wrap items-center gap-2 rounded-md border bg-background p-3 {editable ||
					dragging
						? 'touch-none select-none'
						: ''} {lifted
						? 'z-10 cursor-grabbing shadow-lg ring-2 ring-primary'
						: editable
							? 'cursor-grab hover:border-primary/60'
							: ''}"
					class:lifted
				>
					{#if editable}<span aria-hidden="true" class="text-muted-foreground">⠿</span>{/if}
					<span class="min-w-0 flex-1 break-words">{index + 1}. {pilot.name}</span>
					<Button
						type="button"
						size="sm"
						variant="outline"
						disabled={!editable || index === 0 || dragging !== null}
						aria-label={`Sposta su ${pilot.name}`}
						title={`Sposta su ${pilot.name}`}
						onclick={() => move(pilot.pilot_id, index - 1)}
						><span aria-hidden="true">↑</span></Button
					>
					<Button
						type="button"
						size="sm"
						variant="outline"
						disabled={!editable || index === rows.length - 1 || dragging !== null}
						aria-label={`Sposta giu ${pilot.name}`}
						title={`Sposta giu ${pilot.name}`}
						onclick={() => move(pilot.pilot_id, index + 1)}
						><span aria-hidden="true">↓</span></Button
					>
				</li>
			{/each}
		</ol>
		{#if dirty}<Button
				type="button"
				variant="outline"
				disabled={submitting || store.busy || dragging !== null}
				onclick={() => (discard = edited)}>Scarta ordine locale</Button
			>{/if}
		{#if discard}
			<div class="space-y-2 rounded-md border p-3">
				<p class="text-sm">Scartare le modifiche locali all ordine?</p>
				<div class="flex flex-wrap gap-2">
					<Button
						type="button"
						variant="outline"
						disabled={submitting || store.busy}
						onclick={() => (discard = null)}>Conserva bozza</Button
					>
					<Button
						type="button"
						variant="destructive"
						disabled={submitting || store.busy}
						onclick={discardLocal}>Scarta bozza</Button
					>
				</div>
			</div>
		{/if}
		<div class="flex justify-end">
			<Button type="button" disabled={!editable || dragging !== null} onclick={next}>Avanti</Button>
		</div>
	</section>
{/if}

<style>
	/* La scheda sollevata segue il puntatore senza ritardo; le altre usano flip. */
	.order-row {
		transition:
			box-shadow 120ms ease,
			border-color 120ms ease;
	}
	.order-row.lifted {
		transition: none;
		will-change: transform;
	}
</style>
