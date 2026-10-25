<script lang="ts">
	import type { Snippet } from 'svelte';
	import Modal from '$lib/components/modal.svelte';
	import { Button } from '$lib/components/ui/button';
	import {
		canConfirmDraftCancellation,
		draftClosePolicy,
		proposeDraftCancellation
	} from '$lib/draft-close-policy';
	import type { DraftCancellationProposal } from '$lib/draft-close-policy';
	import type { DraftStore } from '$lib/stores/draft.svelte';

	let {
		open = true,
		store,
		title = 'Preparazione gara',
		externalBusy = false,
		children
	}: {
		open?: boolean;
		store: DraftStore;
		title?: string;
		externalBusy?: boolean;
		children: Snippet;
	} = $props();

	let confirmation = $state.raw<{ owner: DraftStore; proposal: DraftCancellationProposal } | null>(
		null
	);
	let submitting = $state(false);
	let notice = $state<string | null>(null);
	const sessionState = $derived(store.state);
	const policy = $derived(draftClosePolicy(sessionState));
	const visible = $derived(
		open && sessionState.status !== 'finished' && sessionState.status !== 'disposed'
	);
	const canConfirm = $derived(
		!externalBusy &&
			confirmation !== null &&
			confirmation.owner === store &&
			canConfirmDraftCancellation(sessionState, confirmation.proposal)
	);

	$effect(() => {
		if (confirmation && !submitting && !canConfirm) {
			confirmation = null;
			notice = 'Lo stato e cambiato. Riapri la conferma dopo aver verificato i dati.';
		}
	});

	function requestClose(): void {
		if (externalBusy || submitting || confirmation) return;
		store.syncContext();
		const proposal = proposeDraftCancellation(store.state);
		if (!proposal) return;
		notice = null;
		confirmation = { owner: store, proposal };
	}

	/** Ricontrolla istanza e versione e non entra in conflitto con una lettura esterna. */
	async function confirmCancellation(): Promise<void> {
		if (externalBusy || submitting) return;
		const captured = confirmation;
		store.syncContext();
		if (
			!captured ||
			captured.owner !== store ||
			!canConfirmDraftCancellation(store.state, captured.proposal)
		) {
			confirmation = null;
			notice = 'Conferma non piu valida: verifica lo stato corrente.';
			return;
		}
		const target = store;
		submitting = true;
		try {
			const completed = await target.command('cancel', {});
			if (!completed && store === target) {
				notice = 'Annullamento non confermato. Controlla l errore e rileggi se necessario.';
			}
		} finally {
			if (confirmation === captured) confirmation = null;
			submitting = false;
		}
	}

	/** Rilettura esplicita solo quando non ci sono operazioni o conferme concorrenti. */
	async function reload(): Promise<void> {
		if (externalBusy || submitting || confirmation || store.busy) return;
		await store.refresh();
	}
</script>

<Modal
	open={visible}
	{title}
	closeOnOutside={false}
	closePosition="left"
	showClose={policy.showClose}
	closeDisabled={!policy.canRequest || externalBusy || submitting || confirmation !== null}
	wide={sessionState.snapshot?.phase === 'picking' || sessionState.snapshot?.phase === 'decks'}
	stableViewport={sessionState.snapshot?.phase === 'picking' || sessionState.snapshot?.phase === 'decks'}
	onrequestclose={requestClose}
>
	{#if sessionState.error}
		<p role="alert" class="mb-3 text-sm text-destructive">{sessionState.error}</p>
	{/if}
	{#if notice}
		<p role="status" class="mb-3 text-sm">{notice}</p>
	{/if}
	{#if sessionState.status === 'blocked' && !submitting}
		<div class="mb-3">
			<p class="mb-2 text-sm">Lo stato deve essere verificato prima di nuove operazioni.</p>
			<Button variant="outline" disabled={store.busy || externalBusy} onclick={reload}>
				Rileggi dal server
			</Button>
		</div>
	{/if}
	{#if confirmation}
		<div aria-busy={submitting}>
			<p class="text-sm">annullare la gara?</p>
			<p class="mt-2 text-sm text-muted-foreground">
				La procedura verra annullata e le carte ripristinate dal server. Non verra creata una gara.
			</p>
			<div class="mt-4 flex flex-wrap justify-end gap-2">
				<Button variant="outline" disabled={submitting} onclick={() => (confirmation = null)}>
					Non annullare
				</Button>
				<Button
					variant="destructive"
					disabled={submitting || !canConfirm}
					onclick={confirmCancellation}
				>
					{submitting ? 'Annullamento in corso…' : 'Conferma annullamento'}
				</Button>
			</div>
		</div>
	{/if}
	<div
		class:hidden={confirmation !== null}
		inert={confirmation !== null || submitting || store.busy || store.blocked}
	>
		{@render children()}
	</div>
</Modal>
