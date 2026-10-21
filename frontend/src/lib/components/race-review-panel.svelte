<script lang="ts">
	import { onDestroy, onMount, untrack } from 'svelte';
	import { loadPollIntervalMs } from '$lib/card-poll.svelte';
	import ConfirmDialog from '$lib/components/confirm-dialog.svelte';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import ReviewPilotInventory from '$lib/components/review-pilot-inventory.svelte';
	import ReviewIncongruenceDialog from '$lib/components/review-incongruence-dialog.svelte';
	import { ReviewCountsStore } from '$lib/stores/review-counts.svelte';
	import { formatCountdown } from '$lib/race-review-format';

	let {
		championshipId,
		raceId,
		autoOpen = false,
		canOpen = false,
		enabled = true,
		reopen = false,
		onchanged = () => Promise.resolve()
	}: {
		championshipId: number;
		raceId: number;
		autoOpen?: boolean;
		canOpen?: boolean;
		enabled?: boolean;
		reopen?: boolean;
		onchanged?: () => void | Promise<void>;
	} = $props();

	// svelte-ignore state_referenced_locally
	const store = new ReviewCountsStore(championshipId, raceId);
	let disposed = false;
	$effect(() => {
		const allowed = enabled;
		untrack(() => store.setEditingAllowed(allowed));
	});
	let recoveryOpen = $state(false);
	let pending = $state<'reload' | 'start' | 'reopen'>('reload');
	function requestStart(again: boolean): void {
		if (store.pilots.length || store.localBackup || store.serverDraftText) {
			pending = again ? 'reopen' : 'start';
			recoveryOpen = true;
		} else void transition(() => store.start(again));
	}
	async function approveRecovery(): Promise<void> {
		const choice = pending;
		await transition(() =>
			choice === 'reload' ? store.reloadInventory(true) : store.start(choice === 'reopen', true)
		);
	}
	onMount(() => {
		void loadPollIntervalMs()
			.then((intervalMs) => {
				if (!disposed) {
					store.connect(intervalMs);
					if (autoOpen) void store.refreshStatus();
				}
			})
			.catch((cause) => {
				if (!disposed) store.error = String(cause);
			});
	});
	onDestroy(() => {
		disposed = true;
		store.dispose();
	});

	/**
	 * Notifica una transizione riuscita al genitore senza ricaricare il browser.
	 * @param action Azione del negozio di revisione, false se rifiutata o fallita.
	 * @returns Attende azione e callback; errori callback mostrati senza cancellare bozza.
	 * Dopo smontaggio non richiama il genitore; non altera le operazioni del backend.
	 */
	async function transition(action: () => Promise<boolean>): Promise<void> {
		if (!(await action()) || disposed) return;
		try {
			await onchanged();
		} catch (cause) {
			if (!disposed) store.error = cause instanceof Error ? cause.message : 'Errore aggiornamento';
		}
	}
</script>

<Card.Root>
	<Card.Header
		><Card.Title>Revisione degli inventari sponsor</Card.Title><Card.Description
			>Controlla le copie rimaste rispetto al totale avuto, inclusi i bonus S. + ripristina una
			copia; − ne conferma il consumo. Prossimo salva la bozza e spunta il pilota.</Card.Description
		></Card.Header
	>
	<Card.Content class="space-y-4">
		{#if !enabled}<p role="status" class="text-sm text-muted-foreground">
				Lo stato corrente non consente modifiche. La copia resta in sola lettura nella pagina.
			</p>{/if}
		{#if store.active}
			<p class="text-sm" role="timer" aria-live="off">
				Tempo rimasto: {formatCountdown(store.remaining)}
			</p>
			<p class="text-xs text-muted-foreground">
				Alla scadenza il server applica le carte coerenti dell'ultima bozza salvata e lascia
				invariate quelle incongruenti.
			</p>
			<div class="space-y-3">
				{#each store.pilots as pilot, index (pilot.pilot_id)}
					<section class="rounded-lg border p-3">
						<button
							type="button"
							class="flex w-full items-center justify-between gap-2 text-left font-medium"
							aria-expanded={store.index === index}
							disabled={store.busy}
							onclick={() => store.navigate(store.index === index ? -1 : index)}
						>
							<span>{pilot.pilot_name}</span><span
								>{store.checked.includes(pilot.pilot_id) ? '✓ Controllato' : 'Da controllare'} · {store.index ===
								index
									? '−'
									: '+'}</span
							>
						</button>
						{#if store.index === index}<div class="mt-3 space-y-3">
								<ReviewPilotInventory
									{pilot}
									disabled={store.busy || !store.active}
									onadjust={(name, delta) => store.adjust(pilot.pilot_id, name, delta)}
								/>
								<div class="flex flex-wrap justify-between gap-2">
									<Button
										type="button"
										variant="outline"
										disabled={store.busy || index === 0}
										onclick={() => store.navigate(index - 1)}>Indietro</Button
									>
									<Button
										type="button"
										disabled={store.busy}
										onclick={() =>
											store.navigate(index + 1 < store.pilots.length ? index + 1 : -1, true)}
										>{index + 1 < store.pilots.length ? 'Prossimo' : 'Completa controllo'}</Button
									>
								</div>
							</div>{/if}
					</section>
				{/each}
			</div>
			<div class="flex flex-wrap gap-2">
				<Button
					type="button"
					disabled={store.busy || !store.allReviewed}
					onclick={() => transition(() => store.confirm())}>Conferma revisione</Button
				>
				<Button
					type="button"
					variant="outline"
					disabled={store.busy}
					onclick={() => transition(() => store.abandon())}>Salva e rinuncia</Button
				>
			</div>
			<p class="text-sm text-muted-foreground">
				{store.checked.length}/{store.pilots.length} piloti controllati. La conferma richiede tutte le
				spunte.
			</p>
		{:else if store.review?.review_closed_at}
			<p class="text-sm text-green-600">Revisione conclusa.</p>
			{#if canOpen && enabled}<Button
					type="button"
					disabled={store.busy}
					onclick={() => requestStart(true)}>Riapri la revisione</Button
				>{/if}
		{:else if canOpen && enabled}
			<Button type="button" disabled={store.busy} onclick={() => requestStart(reopen)}
				>{reopen ? 'Riapri la revisione' : 'Apri la revisione'}</Button
			>
		{/if}
		{#if store.owned && enabled}<Button
				type="button"
				variant="outline"
				disabled={store.busy}
				onclick={() => {
					pending = 'reload';
					recoveryOpen = true;
				}}>Rileggi inventario</Button
			>{/if}
		{#if store.liveError}<p role="alert" class="text-sm text-destructive">
				Aggiornamento non riuscito: {store.liveError}
			</p>{/if}
		{#if store.blocked}<p role="alert" class="text-sm text-destructive">
				Copia conservata: conferma bloccata. Rileggi con conferma per recuperare.
			</p>{/if}
		{#if store.localIssues.length}<ul class="text-sm">
				{#each store.localIssues as issue (JSON.stringify( [issue.pilotId, issue.cardName, issue.reason] ))}<li
					>
						Pilota {issue.pilotId}, {issue.cardName}: {issue.remaining} copie, totale corrente {issue.total ??
							'non disponibile'} ({issue.reason}).
					</li>{/each}
			</ul>{/if}
		{#if !store.active && store.pilots.length}<details>
				<summary>Conteggi locali in sola lettura</summary
				>{#each store.pilots as pilot (pilot.pilot_id)}<p>
						{pilot.pilot_name}: {pilot.cards
							.map((c) => `${c.card_name} ${c.remaining}/${c.total}`)
							.join(', ')}
					</p>{/each}
			</details>{/if}
		{#if store.previousPilots.length}<details>
				<summary>Copia precedente al recupero</summary
				>{#each store.previousPilots as pilot (pilot.pilot_id)}<p>
						{pilot.pilot_name}: {pilot.cards
							.map((c) => `${c.card_name} ${c.remaining}/${c.total}`)
							.join(', ')}
					</p>{/each}
			</details>{/if}
		{#if store.localBackup}<details>
				<summary>Progresso locale precedente</summary>
				<pre class="overflow-x-auto text-xs">{store.localBackup}</pre>
			</details>{/if}
		{#if store.serverDraftText}<details>
				<summary>Bozza server non applicata</summary>
				<pre class="overflow-x-auto text-xs">{store.serverDraftText}</pre>
			</details>{/if}
		{#if store.error}<p class="text-sm text-destructive" role="alert">{store.error}</p>{/if}
		{#if store.notice}<p class="text-sm text-muted-foreground" role="status">{store.notice}</p>{/if}
		{#if !store.active && store.review && !store.review.review_closed_at}
			<Button
				type="button"
				variant="outline"
				disabled={store.busy}
				onclick={() => transition(() => store.refreshStatus())}>Aggiorna stato</Button
			>
		{/if}
	</Card.Content>
</Card.Root>
<ReviewIncongruenceDialog bind:open={store.conflictOpen} issues={store.issues} />

<ConfirmDialog
	bind:open={recoveryOpen}
	title="Sostituire la copia di lavoro?"
	message="Conteggi locali e spunte saranno sostituiti dopo un backup nel browser. La bozza server verrà riletta; se incompatibile, ripartirai dall'inventario corrente. Nessun conteggio sarà confermato automaticamente. Se il backup non riesce, l'operazione si interrompe."
	confirmLabel={pending === 'reload' ? 'Rileggi' : 'Apri revisione'}
	onconfirm={approveRecovery}
/>
