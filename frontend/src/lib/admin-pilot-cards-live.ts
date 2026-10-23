import { ApiError } from './api';
import { fetchAdminPilotCards } from './admin-pilot-cards-api';
import { subscribeAdminPilotCardsLive, type AdminPilotCardsLiveOptions } from './admin-pilot-cards-live-events';
import { createAdminCardLiveRefresh } from './admin-pilot-cards-live-refresh';
import { blockAdminCardDraftSession, createAdminCardDraftSession, type AdminCardDraftSession } from './admin-pilot-cards-session';
import type { AdminPilotCardsRead } from './admin-pilot-cards-types';

export interface AdminPilotCardLiveOptions {
    championshipId: number;
    pilotId: number;
    getSession: () => AdminCardDraftSession | null;
    isRequestBusy: () => boolean;
    applySession: (session: AdminCardDraftSession) => void;
    onError: (error: unknown) => void;
    onExpired: () => void;
    onStatus?: AdminPilotCardsLiveOptions['onStatus'];
    isCurrent?: () => boolean;
    client?: AdminPilotCardsLiveOptions['client'];
    load?: () => Promise<AdminPilotCardsRead>;
}

/**
 * Collega eventi condivisi, GET autorizzate e sessione senza trasferire carte dagli eventi.
 * @param options Contesto immutabile, accessori correnti e callback sincrone.
 * @returns Invalidazione, notifica dello stato, accettazione server esplicita e cleanup.
 * @throws RangeError per ID invalidi; propaga errori di registrazione dopo cleanup.
 * Le conferme non sono HTTP busy: un segnale puo' invalidarne subito la proposta.
 * Le GET live non sostituiscono una bozza; eventi durante PUT/GET attendono la fine.
 */
export function startAdminPilotCardsLive(options: AdminPilotCardLiveOptions) {
    for (const id of [options.championshipId, options.pilotId]) {
        if (!Number.isSafeInteger(id) || id <= 0) throw new RangeError('Contesto admin non valido');
    }
    let disposed = false;
    let locallyBlocked = false;
    let requested = false;
    let stop = () => {};
    const current = () => !disposed && (options.isCurrent?.() ?? true);

    function validateContext(snapshot: AdminPilotCardsRead): void {
        if (snapshot?.championship_id !== options.championshipId || snapshot?.pilot?.pilot_id !== options.pilotId) {
            throw new Error('Snapshot live di un altro campionato o pilota');
        }
    }
    function block(reason: string): void {
        locallyBlocked = true;
        const session = options.getSession();
        if (session && session.blockedReason === null) options.applySession(blockAdminCardDraftSession(session, reason));
    }

    const refresh = createAdminCardLiveRefresh<AdminCardDraftSession>({
        load: async () => {
            if (!current()) throw new Error('Contesto live scaduto');
            const snapshot = await (options.load ? options.load() : fetchAdminPilotCards(options.championshipId, options.pilotId));
            validateContext(snapshot);
            return createAdminCardDraftSession(snapshot);
        },
        getState: () => {
            const session = options.getSession();
            return {
                busy: options.isRequestBusy(),
                preserve: !current() || locallyBlocked || (session?.transfers.length ?? 0) > 0 || (session !== null && session.blockedReason !== null && !session.baseline.read_only)
            };
        },
        apply: (session) => { if (current()) options.applySession(session); },
        onStale: () => { if (current()) block('Dati remoti cambiati. Bozza conservata: rileggere dal server prima di salvare.'); },
        onError: (cause) => {
            if (!current()) return;
            if (cause instanceof ApiError && cause.status === 401) { expire(); return; }
            block('Aggiornamento live non riuscito. Rileggere il server prima di salvare.');
            options.onError(cause);
        }
    });

    function dispose(): void {
        if (disposed) return;
        disposed = true;
        refresh.dispose();
        stop();
    }
    function expire(): void {
        if (!current()) return;
        block('Sessione scaduta: modifiche bloccate.');
        dispose();
        options.onExpired();
    }
    function invalidate(): Promise<void> {
        if (!current()) return Promise.resolve();
        requested = true;
        return refresh.invalidate();
    }
    function stateChanged(): void { if (current()) refresh.stateChanged(); }

    /**
     * Accetta solo una sessione ottenuta da una PUT o rilettura esplicita utilizzabile.
     * @param next Sessione server gia' validata, non un reset o una bozza locale.
     * @returns Nessun effetto se il contesto e' scaduto.
     * @throws Error per contesto incoerente, prima di sostituire i dati correnti.
     */
    function acceptServerSession(next: AdminCardDraftSession): void {
        if (!current()) return;
        validateContext(next.baseline);
        validateContext(next.preview);
        options.applySession(next);
        locallyBlocked = false;
        refresh.acceptServerSnapshot();
    }

    try {
        if (current()) {
            stop = subscribeAdminPilotCardsLive({
                championshipId: options.championshipId, client: options.client,
                onInvalidate: () => { void invalidate(); },
                onExpired: expire,
                onStatus: (status) => { if (current()) options.onStatus?.(status); }
            });
            if (disposed) stop();
            if (!requested && current()) void invalidate();
        } else dispose();
    } catch (cause) { dispose(); throw cause; }
    return { invalidate, stateChanged, acceptServerSession, dispose };
}
