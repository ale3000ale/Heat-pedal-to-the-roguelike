<script lang="ts">
	import { onDestroy } from 'svelte';
	import { beforeNavigate, goto } from '$app/navigation';
	import { fetchAdminPilotCards } from '$lib/admin-pilot-cards-api';
	import type { AdminCardContainerName } from '$lib/admin-pilot-cards-draft';
	import { appendAdminCardDraftTransfer, createAdminCardDraftSession, resetAdminCardDraftSession, type AdminCardDraftSession } from '$lib/admin-pilot-cards-session';
	import AdminCardContainer from '$lib/components/admin-card-container.svelte';
	import ConfirmDialog from '$lib/components/confirm-dialog.svelte';
	import { Button } from '$lib/components/ui/button';

	let { championshipId, pilotId, onpendingchange }: { championshipId: number; pilotId: number; onpendingchange?: (pending: boolean) => void } = $props();
	let session = $state.raw<AdminCardDraftSession | null>(null);
	let loading = $state(true);
	let loadError = $state<string | null>(null);
	let draftError = $state<string | null>(null);
	let refresh = $state(0);
	let confirmReset = $state(false);
	let confirmLeave = $state(false);
	let leaving = $state(false);
	let nextNavigation = $state<{ url: string; unload: boolean } | null>(null);
	let mounted = true;
	const data = $derived(session?.preview ?? null);
	const pending = $derived((session?.transfers.length ?? 0) > 0);
	const blocked = $derived(session === null || session.blockedReason !== null || leaving);

	function message(cause: unknown): string {
		return cause instanceof Error ? cause.message : 'Operazione locale non riuscita';
	}

	// Il genitore riceve lo stato subito, non tramite un effetto differito.
	function updateSession(next: AdminCardDraftSession | null) {
		session = next;
		onpendingchange?.((next?.transfers.length ?? 0) > 0);
	}

	function move(source: AdminCardContainerName, path: string) {
		if (!session || leaving) return;
		try {
			updateSession(appendAdminCardDraftTransfer(session, { source, path }));
			draftError = null;
		} catch (cause) {
			draftError = message(cause);
		}
	}

	function resetDraft() {
		if (!session || leaving) return;
		try {
			updateSession(resetAdminCardDraftSession(session));
			draftError = null;
		} catch (cause) {
			draftError = message(cause);
		}
	}

	/** Riprende la destinazione confermata; un errore di navigazione conserva la bozza. */
	async function leavePage() {
		const target = nextNavigation;
		if (!target || leaving) return;
		leaving = true;
		if (target.unload) {
			try {
				window.location.assign(target.url);
			} catch (cause) {
				draftError = message(cause);
				leaving = false;
			}
			return;
		}
		const original = session;
		try {
			await goto(target.url);
			// Anche una navigazione che riusa il componente scarta solo dopo il successo.
			if (mounted && original && session === original) {
				updateSession(resetAdminCardDraftSession(original));
			}
		} catch (cause) {
			if (mounted) draftError = message(cause);
		} finally {
			if (mounted) {
				leaving = false;
				nextNavigation = null;
			}
		}
	}

	beforeNavigate((navigation) => {
		if (!pending || leaving) return;
		navigation.cancel();
		// Per chiusura scheda o ricarica senza destinazione interviene il browser.
		if (navigation.to) {
			nextNavigation = { url: navigation.to.url.href, unload: navigation.willUnload };
			confirmLeave = true;
		}
	});

	onDestroy(() => {
		mounted = false;
		onpendingchange?.(false);
	});

	// Le risposte tardive non ripopolano un pannello chiuso o cambiato.
	$effect(() => {
		const championship = championshipId;
		const pilot = pilotId;
		const attempt = refresh;
		let active = true;
		updateSession(null);
		loadError = null;
		draftError = null;
		loading = true;
		void fetchAdminPilotCards(championship, pilot)
			.then((snapshot) => {
				if (active && attempt === refresh) updateSession(createAdminCardDraftSession(snapshot));
			})
			.catch((cause: unknown) => {
				if (active && attempt === refresh) loadError = message(cause);
			})
			.finally(() => {
				if (active && attempt === refresh) loading = false;
			});
		return () => { active = false; };
	});
</script>

<section aria-label="Carte del pilota" aria-busy={loading} class="space-y-4">
	{#if loading}
		<p role="status" class="text-sm text-muted-foreground">Caricamento delle carte…</p>
	{:else if loadError}
		<p role="alert" class="text-sm text-destructive">{loadError}</p>
		<Button variant="outline" onclick={() => (refresh += 1)}>Riprova la lettura</Button>
	{:else if data && session}
		<div class="space-y-2">
			<h3 class="font-semibold">{data.pilot.name}</h3>
			<p class="text-sm text-muted-foreground">Utente: {data.pilot.username}</p>
			<p class="text-sm text-muted-foreground">Bozza locale: un clic sposta una copia. Nessuna modifica viene salvata sul server.</p>
			<p role="status" class="text-sm">Operazioni locali: {session.transfers.length}.</p>
			<Button variant="outline" disabled={!pending || leaving} onclick={() => (confirmReset = true)}>Ripristina bozza</Button>
		</div>
		{#if session.blockedReason !== null}
			<p role="status" class="text-sm">{session.blockedReason}</p>
		{/if}
		{#if draftError}
			<p role="alert" class="text-sm text-destructive">{draftError}</p>
		{/if}
		{#if leaving}<p role="status" class="text-sm">Navigazione in corso…</p>{/if}
		<div class="grid gap-4 md:grid-cols-2">
			<div class="space-y-3">
				<h4 class="font-semibold">Carte del pilota</h4>
				<AdminCardContainer title="Mazzo da gioco" deck={data.containers.game_deck} gameDeck destination="Pool Modifiche" disabled={blocked || !data.containers.modification_pool.available} onmove={(path) => move('game_deck', path)} />
				<AdminCardContainer title="Inventario Modifiche" deck={data.containers.modification_inventory} destination="Pool Modifiche" disabled={blocked || !data.containers.modification_pool.available} onmove={(path) => move('modification_inventory', path)} />
				<AdminCardContainer title="Inventario Sponsor" deck={data.containers.sponsor_inventory} destination="Pool Sponsor" disabled={blocked || !data.containers.sponsor_pool.available} onmove={(path) => move('sponsor_inventory', path)} />
			</div>
			<div class="space-y-3">
				<h4 class="font-semibold">Pool del campionato</h4>
				<AdminCardContainer title="Pool Modifiche" deck={data.containers.modification_pool} destination="Inventario Modifiche" disabled={blocked || !data.containers.modification_inventory.available} onmove={(path) => move('modification_pool', path)} />
				<AdminCardContainer title="Pool Sponsor" deck={data.containers.sponsor_pool} destination="Inventario Sponsor" disabled={blocked || !data.containers.sponsor_inventory.available} onmove={(path) => move('sponsor_pool', path)} />
			</div>
		</div>
	{/if}
</section>

{#if confirmReset}
	<ConfirmDialog bind:open={confirmReset} title="Ripristinare la bozza?" message="Le operazioni locali verranno scartate. Verrà ripristinata la lettura iniziale, senza rileggere o modificare il server." confirmLabel="Scarta e ripristina" onconfirm={resetDraft} />
{/if}
{#if confirmLeave}
	<ConfirmDialog bind:open={confirmLeave} title="Abbandonare la bozza?" message="La bozza non è salvata. Proseguendo la navigazione le operazioni locali verranno scartate." confirmLabel="Scarta e prosegui" onconfirm={leavePage} />
{/if}
