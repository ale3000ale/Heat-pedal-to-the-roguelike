<script lang="ts">
	import { tick, type Snippet } from 'svelte';
	import Modal from '$lib/components/modal.svelte';
	import { Button } from '$lib/components/ui/button';
	import {
		canConfirmDraftCancellation,
		draftCancellationExpired,
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
	let keepButton = $state<HTMLButtonElement | null>(null);
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
	/** Carte gia assegnate che il server restituira al pool. */
	const chosen = $derived(sessionState.snapshot?.picks.length ?? 0);
	/** Riquadro ampio solo per carte e mazzi: la conferma usa la misura del suo messaggio.
	 * La scelta carte si adatta al proprio riquadro; i mazzi tengono l'altezza stabile.
	 */
	const expanded = $derived(
		confirmation === null &&
			(sessionState.snapshot?.phase === 'picking' || sessionState.snapshot?.phase === 'decks')
	);
	let content = $state<HTMLDivElement | null>(null);
	/** Scroll del dialog prima della conferma, ripristinato quando si torna alla gara. */
	let savedScroll: number | null = null;

	$effect(() => {
		if (confirmation !== null || savedScroll === null) return;
		const top = savedScroll;
		savedScroll = null;
		void tick().then(() => {
			const dialog = content?.closest<HTMLElement>('[role="dialog"]');
			if (dialog) dialog.scrollTop = top;
		});
	});

	// Solo una scadenza definitiva chiude la conferma: versioni e letture in corso no.
	$effect(() => {
		if (
			confirmation &&
			!submitting &&
			(confirmation.owner !== store ||
				draftCancellationExpired(sessionState, confirmation.proposal))
		) {
			confirmation = null;
			notice = 'Annullamento non piu disponibile: verifica lo stato corrente.';
		}
	});

	// Il focus parte dall'opzione sicura, cosi Invio non annulla per errore.
	$effect(() => {
		if (confirmation && keepButton) keepButton.focus();
	});

	function requestClose(): void {
		if (externalBusy || submitting || confirmation) return;
		store.syncContext();
		const proposal = proposeDraftCancellation(store.state);
		if (!proposal) return;
		notice = null;
		savedScroll = content?.closest<HTMLElement>('[role="dialog"]')?.scrollTop ?? null;
		confirmation = { owner: store, proposal };
	}

	function keepDraft(): void {
		if (submitting) return;
		confirmation = null;
	}

	/** Esc chiude solo la conferma: la procedura resta aperta come da specifica. */
	function onkeydown(event: KeyboardEvent): void {
		if (event.key === 'Escape' && confirmation && !submitting) {
			event.preventDefault();
			keepDraft();
		}
	}

	/** Ricontrolla istanza e draft; la conferma resta aperta se il server rifiuta. */
	async function confirmCancellation(): Promise<void> {
		if (externalBusy || submitting) return;
		const captured = confirmation;
		store.syncContext();
		if (
			!captured ||
			captured.owner !== store ||
			!canConfirmDraftCancellation(store.state, captured.proposal)
		)
			return;
		const target = store;
		submitting = true;
		notice = null;
		try {
			const completed = await target.command('cancel', {});
			if (!completed && store === target) {
				notice = 'Annullamento non confermato dal server. Puoi riprovare o tornare alla gara.';
			}
		} finally {
			submitting = false;
		}
	}

	/** Rilettura esplicita solo quando non ci sono operazioni o conferme concorrenti. */
	async function reload(): Promise<void> {
		if (externalBusy || submitting || confirmation || store.busy) return;
		await store.refresh();
	}
</script>

<svelte:window {onkeydown} />

<Modal
	open={visible}
	{title}
	closeOnOutside={false}
	closePosition="left"
	showClose={policy.showClose}
	closeDisabled={!policy.canRequest || externalBusy || submitting || confirmation !== null}
	wide={expanded}
	stableViewport={expanded && sessionState.snapshot?.phase === 'decks'}
	fitContent={expanded && sessionState.snapshot?.phase === 'picking'}
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
		<div
			role="alertdialog"
			aria-labelledby="draft-cancel-title"
			aria-describedby="draft-cancel-details"
			aria-busy={submitting}
			class="rounded-md border border-destructive/40 bg-destructive/5 p-4"
		>
			<p id="draft-cancel-title" class="font-semibold">Annullare la gara?</p>
			<div id="draft-cancel-details" class="mt-2 space-y-1 text-sm text-muted-foreground">
				<p>La preparazione verra chiusa per tutti i partecipanti e non verra creata alcuna gara.</p>
				<p>
					{chosen === 0
						? 'Pool, inventari e mazzi restano come prima della preparazione.'
						: `${chosen === 1 ? 'La carta gia scelta torna' : `Le ${chosen} carte gia scelte tornano`} nel pool; inventari e mazzi vengono ripristinati.`}
				</p>
			</div>
			{#if !canConfirm && !submitting}
				<p role="status" class="mt-2 text-sm text-muted-foreground">In attesa del server…</p>
			{/if}
			<div class="mt-4 flex flex-wrap justify-end gap-2">
				<Button bind:ref={keepButton} variant="outline" disabled={submitting} onclick={keepDraft}>
					Non annullare
				</Button>
				<Button
					variant="destructive"
					disabled={submitting || !canConfirm}
					onclick={confirmCancellation}
				>
					{submitting ? 'Annullamento in corso…' : 'Annulla la gara'}
				</Button>
			</div>
			<p class="mt-2 text-right text-xs text-muted-foreground">Esc per tornare alla gara</p>
		</div>
	{/if}
	<div
		bind:this={content}
		class:hidden={confirmation !== null}
		inert={confirmation !== null || submitting || store.busy || store.blocked}
	>
		{@render children()}
	</div>
</Modal>
