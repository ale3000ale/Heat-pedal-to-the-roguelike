<script lang="ts">
    import { onDestroy } from 'svelte';
    import { ApiError } from '$lib/api';
    import { fetchAdminPilotCards } from '$lib/admin-pilot-cards-api';
    import { saveAdminPilotCards } from '$lib/admin-pilot-cards-save-api';
    import { prepareAdminCardSave, type AdminCardSavePlan } from '$lib/admin-pilot-cards-save-plan';
    import { blockAdminCardDraftSession, createAdminCardDraftSession, type AdminCardDraftSession } from '$lib/admin-pilot-cards-session';
    import Modal from '$lib/components/modal.svelte';
    import { Button } from '$lib/components/ui/button';

    let { championshipId, pilotId, session, disabled = false, onchange, onserverchange, onbusychange, onrequestchange }: {
        championshipId: number; pilotId: number; session: AdminCardDraftSession; disabled?: boolean;
        onchange: (next: AdminCardDraftSession) => void;
        onserverchange?: (next: AdminCardDraftSession) => void;
        onbusychange: (busy: boolean) => void;
        onrequestchange?: (busy: boolean) => void;
    } = $props();
    let prepared = $state.raw<{ original: AdminCardDraftSession; plan: AdminCardSavePlan } | null>(null);
    let busy = $state(false);
    let confirmSave = $state(false);
    let confirmReload = $state(false);
    let error = $state<string | null>(null);
    let status = $state('');
    let notice = $state('');
    let noticeSession = $state.raw<AdminCardDraftSession | null>(null);
    let active = true;
    const locked = $derived(disabled || busy || confirmSave || confirmReload);
    const cannotSave = $derived(locked || session.blockedReason !== null || session.baseline.read_only || session.transfers.length === 0);

    function message(cause: unknown): string { return cause instanceof Error ? cause.message : 'Operazione non riuscita'; }
    function applyServer(next: AdminCardDraftSession) { if (onserverchange) onserverchange(next); else onchange(next); }
    function cancelSave() { if (busy) return; confirmSave = false; prepared = null; onbusychange(false); }
    function cancelReload() { if (busy) return; confirmReload = false; onbusychange(false); }
    function requestSave() {
        if (cannotSave) return;
        error = null;
        try { prepared = { original: session, plan: prepareAdminCardSave(session) }; confirmSave = true; onbusychange(true); }
        catch (cause) { error = message(cause); }
    }

    /** Consuma una sola proposta; solo una risposta server utilizzabile sblocca il live. */
    async function submitSave() {
        const proposal = prepared;
        if (!proposal || busy || disabled) return;
        if (session !== proposal.original || session.blockedReason !== null || session.baseline.read_only) {
            cancelSave(); error = 'La bozza è cambiata: aprire nuovamente il riepilogo.'; return;
        }
        prepared = null; confirmSave = false; busy = true;
        status = 'Salvataggio in corso…';
        onrequestchange?.(true); onbusychange(true); error = null;
        try {
            const snapshot = await saveAdminPilotCards(championshipId, pilotId, proposal.plan.request);
            if (!active || session !== proposal.original) return;
            const next = createAdminCardDraftSession(snapshot);
            applyServer(next); noticeSession = next; notice = 'Modifiche salvate.';
        } catch (cause) {
            if (!active || session !== proposal.original) return;
            error = message(cause);
            if (!(cause instanceof ApiError && cause.status === 422)) {
                const reason = cause instanceof ApiError && [401, 403, 404, 409].includes(cause.status)
                    ? `Salvataggio bloccato: ${error}. Rileggere il server prima di un nuovo invio.`
                    : 'Esito del salvataggio non verificato. Il server potrebbe avere applicato le modifiche: rileggere prima di un nuovo invio.';
                onchange(blockAdminCardDraftSession(proposal.original, reason));
            }
        } finally { if (active) { busy = false; onrequestchange?.(false); onbusychange(false); } }
    }
    function requestReload() {
        if (locked) return;
        if (session.transfers.length > 0) { confirmReload = true; onbusychange(true); }
        else void reload();
    }

    /** Rilettura esplicita: su errore conserva la sessione e non sblocca il coordinatore. */
    async function reload() {
        if (busy || disabled) return;
        const original = session;
        confirmReload = false; busy = true; status = 'Rilettura del server in corso…';
        onrequestchange?.(true); onbusychange(true); error = null;
        try {
            const snapshot = await fetchAdminPilotCards(championshipId, pilotId);
            if (!active || session !== original) return;
            const next = createAdminCardDraftSession(snapshot);
            applyServer(next); noticeSession = next; notice = 'Dati riletti dal server.';
        } catch (cause) { if (active && session === original) error = message(cause); }
        finally { if (active) { busy = false; onrequestchange?.(false); onbusychange(false); } }
    }
    onDestroy(() => { active = false; onrequestchange?.(false); onbusychange(false); });
</script>

<div class="space-y-2" aria-busy={busy}>
    <div class="flex flex-wrap gap-2">
        <Button disabled={cannotSave} onclick={requestSave}>Riepilogo e salva</Button>
        <Button variant="outline" disabled={locked} onclick={requestReload}>Rileggi dal server</Button>
    </div>
    {#if busy}<p role="status" class="text-sm">{status}</p>{/if}
    {#if error}<p role="alert" class="text-sm text-destructive">{error}</p>{/if}
    {#if noticeSession === session && notice}<p role="status" class="text-sm">{notice}</p>{/if}
</div>
{#if confirmSave && prepared}
    <Modal open title="Confermare il salvataggio?" onrequestclose={cancelSave}>
        <p class="text-sm">Conferma queste operazioni per {prepared.plan.preview.pilot.name}. Nessun invio è stato ancora eseguito.</p>
        <ol class="mt-3 list-decimal space-y-2 pl-5 text-sm">{#each prepared.plan.summary as line, index (index)}<li>{line}</li>{/each}</ol>
        <div class="mt-4 flex flex-wrap justify-end gap-2"><Button variant="outline" onclick={cancelSave}>Annulla</Button><Button disabled={busy} onclick={submitSave}>Conferma e salva</Button></div>
    </Modal>
{/if}
{#if confirmReload}
    <Modal open title="Scartare la bozza e rileggere?" onrequestclose={cancelReload}>
        <p class="text-sm">Le operazioni locali saranno scartate solo se la lettura dal server riesce. La rilettura non invia modifiche.</p>
        <div class="mt-4 flex flex-wrap justify-end gap-2"><Button variant="outline" onclick={cancelReload}>Annulla</Button><Button variant="destructive" disabled={busy} onclick={reload}>Scarta e rileggi</Button></div>
    </Modal>
{/if}
