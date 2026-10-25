<script lang="ts">
	import { untrack, type Snippet } from 'svelte';
	import { auth } from '$lib/auth.svelte';
	import type { DraftHost } from '$lib/draft-host-context';
	import type { DraftHostCompletion } from '$lib/draft-host';
	import type { DraftStore } from '$lib/stores/draft.svelte';
	import { blockDraftEscape, reconcileDraftQueue, selectDraftEntry } from '$lib/draft-host-view';
	import { draftHostFocus } from '$lib/draft-host-focus';
	import DraftFlow from '$lib/components/draft-flow.svelte';
	import { Button } from '$lib/components/ui/button';

	let { host, children }: { host: DraftHost; children: Snippet } = $props();
	const empty: readonly DraftStore[] = [];
	let queue = $state.raw<readonly DraftStore[]>(empty);
	let queueKey = $state<string | null>(null);
	let notice = $state.raw<{ key: string; values: DraftHostCompletion[] } | null>(null);
	const contextKey = $derived(auth.sessionKey);
	const current = $derived(contextKey !== null && $host.contextKey === contextKey);
	const ordered = $derived(current ? reconcileDraftQueue(queueKey === contextKey ? queue : empty, $host.entries) : empty);
	const selected = $derived(current ? selectDraftEntry(ordered, $host.entries) : null);
	const blocking = $derived(selected !== null);
	const busy = $derived($host.busy || $host.entries.some((entry) => entry.store.busy));
	const problem = $derived(current ? $host.error ?? $host.entries.map((entry) => entry.store.state).find((root) => root.status === 'blocked')?.error ?? null : null);

	// Le pre-effect precedono il cleanup DOM di DraftFlow, che dismette il suo store.
	// Gli esiti vengono quindi copiati nel registro prima che quello snapshot scompaia.
	$effect.pre(() => {
		const key = contextKey;
		for (const entry of $host.entries) void entry.store.state.status;
		const owner = host;
		untrack(() => {
			if (notice && notice.key !== key) notice = null;
			owner.sync();
		});
	});

	// Una sola lettura iniziale per chiave; non dipende da pagina, coda o snapshot.
	$effect(() => {
		const key = contextKey;
		const owner = host;
		untrack(() => {
			owner.sync();
			if (key) void owner.refresh();
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

	/** Recupero manuale del registro, mai un reinvio dei comandi con esito incerto. */
	async function reload(): Promise<void> {
		if (!contextKey || busy) return;
		await host.refresh();
	}
</script>

<svelte:window onkeydowncapture={(event) => blockDraftEscape(event, blocking)} />

<div inert={blocking} aria-hidden={blocking ? true : undefined}>
	{@render children()}
</div>

{#snippet recoveryNotice()}
	<aside class="fixed top-3 right-3 left-3 z-[70] mx-auto max-w-xl rounded-lg border border-destructive bg-background p-3 shadow-lg" aria-label="Recupero preparazioni">
		<p role="alert" class="mb-2 text-sm">{problem}</p>
		<Button type="button" variant="outline" disabled={busy} onclick={reload}>Rileggi preparazioni</Button>
	</aside>
{/snippet}

{#if selected}
	{#key selected.store}
		<section data-draft-host-dialog tabindex="-1" aria-label="Flusso di preparazione gara" class="relative z-[60] outline-none" use:draftHostFocus>
			{#if problem}{@render recoveryNotice()}{/if}
			<DraftFlow store={selected.store} />
		</section>
	{/key}
{:else if problem}
	{@render recoveryNotice()}
{/if}

{#if !blocking && notice && notice.key === contextKey}
	<div role="status" class="fixed right-3 bottom-3 left-3 z-40 mx-auto max-w-xl rounded-lg border bg-background p-3 text-sm shadow-lg">
		{#each notice.values as result (result.draftId)}
			<p>{result.kind === 'race' ? `Gara ${result.raceId} creata per il campionato ${result.championshipId}.` : `Preparazione del campionato ${result.championshipId} annullata.`}</p>
		{/each}
	</div>
{/if}
