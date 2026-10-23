<script lang="ts">
    import { onDestroy, untrack } from 'svelte';
    import { beforeNavigate, goto } from '$app/navigation';
    import { auth } from '$lib/auth.svelte';
    import { startAdminPilotCardsLive } from '$lib/admin-pilot-cards-live';
    import type { AdminCardContainerName } from '$lib/admin-pilot-cards-draft';
    import { appendAdminCardDraftTransfer, resetAdminCardDraftSession, type AdminCardDraftSession } from '$lib/admin-pilot-cards-session';
    import type { ConnectionStatus } from '$lib/events/event-types';
    import AdminCardContainer from '$lib/components/admin-card-container.svelte';
    import AdminPilotCardsSaveControls from '$lib/components/admin-pilot-cards-save-controls.svelte';
    import ConfirmDialog from '$lib/components/confirm-dialog.svelte';
    import { Button } from '$lib/components/ui/button';

    let { championshipId, pilotId, onpendingchange, onbusychange }: { championshipId: number; pilotId: number; onpendingchange?: (pending: boolean) => void; onbusychange?: (busy: boolean) => void } = $props();
    let session = $state.raw<AdminCardDraftSession | null>(null);
    let loading = $state(true);
    let busy = $state(false);
    let requestBusy = $state(false);
    let ownerId = $state<number | null>(null);
    let liveStatus = $state<ConnectionStatus>('stopped');
    let loadError = $state<string | null>(null);
    let draftError = $state<string | null>(null);
    let refresh = $state(0);
    let confirmReset = $state(false);
    let confirmLeave = $state(false);
    let leaving = $state(false);
    let nextNavigation = $state<{ url: string; unload: boolean } | null>(null);
    let mounted = true;
    let live: ReturnType<typeof startAdminPilotCardsLive> | null = null;
    const data = $derived(session?.preview ?? null);
    const pending = $derived((session?.transfers.length ?? 0) > 0);
    const unauthorized = $derived(!auth.isAdmin || auth.user?.id !== ownerId);
    const blocked = $derived(session === null || session.blockedReason !== null || leaving || busy || unauthorized);
    const statusLabels: Record<ConnectionStatus, string> = { stopped: 'ferma', connecting: 'connessione in corso', open: 'attiva', retrying: 'riconnessione in corso', unsupported: 'non disponibile', expired: 'sessione scaduta' };

    function message(cause: unknown): string { return cause instanceof Error ? cause.message : 'Operazione locale non riuscita'; }
    function updateSession(next: AdminCardDraftSession | null) { session = next; onpendingchange?.((next?.transfers.length ?? 0) > 0); live?.stateChanged(); }
    function acceptServerSession(next: AdminCardDraftSession) { live?.acceptServerSession(next); draftError = null; }
    function handleBusyChange(value: boolean) { busy = value; onbusychange?.(value); }
    function handleRequestChange(value: boolean) { requestBusy = value; live?.stateChanged(); }
    function move(source: AdminCardContainerName, path: string) {
        if (!session || blocked) return;
        try { updateSession(appendAdminCardDraftTransfer(session, { source, path })); draftError = null; } catch (cause) { draftError = message(cause); }
    }
    function resetDraft() {
        if (!session || leaving || busy || unauthorized) return;
        try { updateSession(resetAdminCardDraftSession(session)); draftError = null; } catch (cause) { draftError = message(cause); }
    }
    async function leavePage() {
        const target = nextNavigation; if (!target || leaving || busy) return;
        leaving = true; live?.stateChanged();
        if (target.unload) {
            try { window.location.assign(target.url); } catch (cause) { draftError = message(cause); leaving = false; live?.stateChanged(); }
            return;
        }
        const original = session;
        try {
            // URL completa gia' fornita da SvelteKit, non una rotta da costruire.
            // eslint-disable-next-line svelte/no-navigation-without-resolve
            await goto(target.url);
            if (mounted && original && session === original) updateSession(resetAdminCardDraftSession(original));
        } catch (cause) { if (mounted) draftError = message(cause); }
        finally { if (mounted) { leaving = false; nextNavigation = null; live?.stateChanged(); } }
    }
    beforeNavigate((navigation) => {
        if (busy) { navigation.cancel(); return; }
        if (!pending || leaving) return;
        navigation.cancel();
        if (navigation.to) { nextNavigation = { url: navigation.to.url.href, unload: navigation.willUnload }; confirmLeave = true; }
    });
    onDestroy(() => { mounted = false; live?.dispose(); live = null; onpendingchange?.(false); onbusychange?.(false); });
    $effect(() => {
        const championship = championshipId; const pilot = pilotId;
        const userId = auth.user?.id ?? null; const admin = auth.isAdmin; const attempt = refresh;
        return untrack(() => {
            live = null; ownerId = userId; requestBusy = false; busy = false; onbusychange?.(false);
            confirmReset = false; confirmLeave = false; leaving = false; updateSession(null);
            loadError = null; draftError = null; loading = true; liveStatus = 'stopped';
            if (!admin || userId === null) { loading = false; loadError = 'Accesso amministratore richiesto'; return; }
            const controller = startAdminPilotCardsLive({
                championshipId: championship, pilotId: pilot,
                isCurrent: () => mounted && auth.isAdmin && auth.user?.id === userId && championshipId === championship && pilotId === pilot,
                getSession: () => session, isRequestBusy: () => requestBusy || leaving,
                applySession: (next) => { updateSession(next); loading = false; loadError = null; },
                onError: (cause) => { loading = false; if (session === null) loadError = message(cause); else draftError = message(cause); },
                onExpired: () => { loading = false; const text = 'Sessione scaduta: riaprire il pannello dopo l’accesso.'; if (session === null) loadError = text; else draftError = text; },
                onStatus: (status) => { liveStatus = status; }
            });
            live = controller;
            return () => { controller.dispose(); if (live === controller) live = null; void attempt; };
        });
    });
</script>

<section aria-label="Carte del pilota" aria-busy={loading || busy} class="space-y-4">
    <p class="text-sm text-muted-foreground">Connessione live: {statusLabels[liveStatus]}. Lo stato della connessione non conferma la freschezza dei dati.</p>
    {#if loading}
        <p role="status" class="text-sm text-muted-foreground">Caricamento delle carte…</p>
    {:else if loadError}
        <p role="alert" class="text-sm text-destructive">{loadError}</p>
        <Button variant="outline" onclick={() => (refresh += 1)}>Riprova la lettura</Button>
    {:else if data && session}
        <div class="space-y-2">
            <h3 class="font-semibold">{data.pilot.name}</h3>
            <p class="text-sm text-muted-foreground">Utente: {data.pilot.username}</p>
            <p class="text-sm text-muted-foreground">Le modifiche restano locali fino a «Conferma e salva».</p>
            <p role="status" class="text-sm">Operazioni locali: {session.transfers.length}.</p>
            <Button variant="outline" disabled={!pending || leaving || busy || unauthorized} onclick={() => (confirmReset = true)}>Ripristina bozza</Button>
        </div>
        {#if session.blockedReason !== null}<p role="status" class="text-sm">{session.blockedReason}</p>{/if}
        {#if draftError}<p role="alert" class="text-sm text-destructive">{draftError}</p>{/if}
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
        <div class="flex justify-end border-t pt-4">
            <AdminPilotCardsSaveControls {championshipId} {pilotId} {session} disabled={leaving || confirmReset || confirmLeave || unauthorized} onchange={updateSession} onserverchange={acceptServerSession} onbusychange={handleBusyChange} onrequestchange={handleRequestChange} />
        </div>
    {/if}
</section>
{#if confirmReset}
    <ConfirmDialog bind:open={confirmReset} title="Ripristinare la bozza?" message="Le operazioni locali verranno scartate. Verrà ripristinata la lettura iniziale, senza rileggere o modificare il server." confirmLabel="Scarta e ripristina" onconfirm={resetDraft} />
{/if}
{#if confirmLeave}
    <ConfirmDialog bind:open={confirmLeave} title="Abbandonare la bozza?" message="La bozza non è salvata. Proseguendo la navigazione le operazioni locali verranno scartate." confirmLabel="Scarta e prosegui" onconfirm={leavePage} />
{/if}
