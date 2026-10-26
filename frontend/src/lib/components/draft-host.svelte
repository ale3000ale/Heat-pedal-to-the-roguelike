<script lang="ts">
	import { tick, untrack, type Snippet } from 'svelte';
	import { auth } from '$lib/auth.svelte';
	import type { DraftHost } from '$lib/draft-host-context';
	import type { DraftHostCompletion } from '$lib/draft-host';
	import type { DraftDeckSession } from '$lib/draft-deck-session';
	import type { DraftStore } from '$lib/stores/draft.svelte';
	import { blockDraftEscape, reconcileDraftQueue, selectDraftEntry } from '$lib/draft-host-view';
	import { draftHostFocus } from '$lib/draft-host-focus';
	import { startDraftLive } from '$lib/draft-live';
	import { createDraftLiveDeckRefresh } from '$lib/draft-live-deck';
	import DraftFlow from '$lib/components/draft-flow.svelte';
	import { Button } from '$lib/components/ui/button';

	let { host, children }: { host: DraftHost; children: Snippet } = $props();
	const empty: readonly DraftStore[] = [];
	const deckRefresh = createDraftLiveDeckRefresh();
	let queue = $state.raw<readonly DraftStore[]>(empty);
	let queueKey = $state<string | null>(null);
	let notice = $state.raw<{ key: string; values: DraftHostCompletion[] } | null>(null);
	let coordinator = $state.raw<{
		owner: DraftStore;
		decks: DraftDeckSession;
		busy: boolean;
	} | null>(null);
	let live = $state.raw<ReturnType<typeof startDraftLive> | null>(null);
	let liveError = $state<string | null>(null);
	const contextKey = $derived(auth.sessionKey);
	const current = $derived(contextKey !== null && $host.contextKey === contextKey);
	const ordered = $derived(
		current ? reconcileDraftQueue(queueKey === contextKey ? queue : empty, $host.entries) : empty
	);
	const selected = $derived(current ? selectDraftEntry(ordered, $host.entries) : null);
	const blocking = $derived(selected !== null);
	const detailsBusy = $derived(
		coordinator?.owner === selected?.store && coordinator !== null && coordinator.busy
	);
	const busy = $derived(
		$host.busy || detailsBusy || $host.entries.some((entry) => entry.store.busy)
	);
	const problem = $derived(
		current
			? ($host.error ??
					liveError ??
					$host.entries.map((entry) => entry.store.state).find((root) => root.status === 'blocked')
						?.error ??
					null)
			: null
	);

	$effect.pre(() => {
		const key = contextKey;
		for (const entry of $host.entries) void entry.store.state.status;
		const owner = host;
		untrack(() => {
			if (notice && notice.key !== key) notice = null;
			if (!key) coordinator = null;
			owner.sync();
		});
	});
	$effect(() => {
		const key = contextKey;
		const owner = host;
		const binding = untrack(() => {
			owner.sync();
			liveError = null;
			if (!key) return null;
			const value = startDraftLive({
				host: owner,
				getContextKey: () => auth.sessionKey,
				isBusy: () => detailsBusy,
				onError: (cause) => {
					if (auth.sessionKey === key)
						liveError =
							cause instanceof Error ? cause.message : 'Sincronizzazione draft non riuscita';
				},
				afterRefresh: async () => {
					// Aspetta l'aggiornamento dei figli, incluso il loro caricamento iniziale.
					await tick();
					if (auth.sessionKey !== key) return;
					const detail = coordinator;
					if (detail && detail.owner === selected?.store)
						await deckRefresh.refresh(detail.owner, detail.decks);
				}
			});
			live = value;
			return value;
		});
		return () =>
			untrack(() => {
				binding?.dispose();
				if (live === binding) live = null;
			});
	});
	$effect(() => {
		void busy;
		const binding = live;
		untrack(() => {
			void binding?.wake();
		});
	});
	$effect(() => {
		const next = ordered;
		const key = contextKey;
		untrack(() => {
			if (queue !== next) queue = next;
			if (queueKey !== key) queueKey = key;
		});
	});
	$effect(() => {
		const key = contextKey;
		const matching = current;
		const count = $host.completions.length;
		if (!key || !matching || count === 0) return;
		untrack(() => {
			const values = host.takeCompletions();
			if (values.length) notice = { key, values };
		});
	});
	$effect(() => {
		const owner = host;
		return () => untrack(() => owner.dispose());
	});

	/** Ignora notifiche di cleanup appartenenti a un altro flusso. */
	function updateDecks(owner: DraftStore, decks: DraftDeckSession | null, loading: boolean): void {
		if (selected?.store === owner && decks) coordinator = { owner, decks, busy: loading };
		else if (coordinator?.owner === owner) coordinator = null;
	}
	/** Recupero manuale accodato, mai reinvio di un POST. */
	async function reload(): Promise<void> {
		if (!contextKey || busy) return;
		liveError = null;
		if (live) await live.request();
		else await host.refresh();
	}
</script>

<svelte:window onkeydowncapture={(event) => blockDraftEscape(event, blocking)} />
<div inert={blocking} aria-hidden={blocking ? true : undefined}>
	{@render children()}
</div>

{#snippet recoveryNotice()}
	<aside
		class="fixed top-3 right-3 left-3 z-[70] mx-auto max-w-xl rounded-lg border border-destructive bg-background p-3 shadow-lg"
		aria-label="Recupero preparazioni"
	>
		<p role="alert" class="mb-2 text-sm">{problem}</p>
		<Button type="button" variant="outline" disabled={busy} onclick={reload}
			>Rileggi preparazioni</Button
		>
	</aside>
{/snippet}

{#if selected}
	<!-- La versione e gli oggetti dei DTO non definiscono il ciclo di vita del dialog. -->
	{#key `${contextKey}:${selected.id}`}
		<section
			data-draft-host-dialog
			tabindex="-1"
			aria-label="Flusso di preparazione gara"
			class="relative z-[60] outline-none"
			use:draftHostFocus
		>
			{#if problem}{@render recoveryNotice()}{/if}
			<DraftFlow store={selected.store} ondecks={updateDecks} />
		</section>
	{/key}
{:else if problem}
	{@render recoveryNotice()}
{/if}

{#if !blocking && notice && notice.key === contextKey}
	<div
		role="status"
		class="fixed right-3 bottom-3 left-3 z-40 mx-auto max-w-xl rounded-lg border bg-background p-3 text-sm shadow-lg"
	>
		{#each notice.values as result (result.draftId)}
			<p>
				{result.kind === 'race'
					? `Gara ${result.raceId} creata per il campionato ${result.championshipId}.`
					: `Preparazione del campionato ${result.championshipId} annullata.`}
			</p>
		{/each}
	</div>
{/if}
