import {
	AdminCardDraftError,
	planAdminCardTransfers,
	type AdminCardTransfer
} from './admin-pilot-cards-draft';
import type { AdminPilotCardsRead } from './admin-pilot-cards-types';

/** Stato locale: non e' una sessione di autenticazione o una transazione backend. */
export interface AdminCardDraftSession {
	baseline: AdminPilotCardsRead;
	preview: AdminPilotCardsRead;
	transfers: AdminCardTransfer[];
	blockedReason: string | null;
}

/** Clona tutti i dati della sessione, inclusi anteprima e registro dei clic. */
function copySession(session: AdminCardDraftSession): AdminCardDraftSession {
	return {
		baseline: planAdminCardTransfers(session.baseline, []),
		preview: planAdminCardTransfers(session.preview, []),
		transfers: session.transfers.map((transfer) => ({ ...transfer })),
		blockedReason: session.blockedReason
	};
}

/**
 * Inizia una bozza indipendente dal DTO ricevuto, senza autorizzare scritture.
 * @param snapshot Snapshot iniziale letto dal backend.
 * @returns Baseline, anteprima indipendente, registro vuoto e blocco iniziale.
 * @throws AdminCardDraftError se le carte dello snapshot non sono valide.
 */
export function createAdminCardDraftSession(snapshot: AdminPilotCardsRead): AdminCardDraftSession {
	const baseline = planAdminCardTransfers(snapshot, []);
	return {
		baseline,
		preview: planAdminCardTransfers(baseline, []),
		transfers: [],
		blockedReason: snapshot.read_only
			? (snapshot.blocked_reason ?? 'Modifiche bloccate dal backend')
			: null
	};
}

/**
 * Aggiunge un clic e ricalcola la bozza dalla baseline, non da una vista mutata.
 * @param session Stato locale corrente, che non viene modificato.
 * @param transfer Sorgente e percorso della carta, una sola copia.
 * @returns Nuova sessione solo se l'intera sequenza e' applicabile.
 * @throws AdminCardDraftError su blocco o trasferimento non applicabile.
 */
export function appendAdminCardDraftTransfer(
	session: AdminCardDraftSession,
	transfer: AdminCardTransfer
): AdminCardDraftSession {
	if (session.blockedReason !== null) {
		throw new AdminCardDraftError(session.blockedReason);
	}
	const transfers = [...session.transfers.map((item) => ({ ...item })), { ...transfer }];
	const baseline = planAdminCardTransfers(session.baseline, []);
	const preview = planAdminCardTransfers(baseline, transfers);
	return { baseline, preview, transfers, blockedReason: null };
}

/**
 * Blocca ulteriori clic senza perdere bozza, baseline, versioni o operazioni.
 * @param session Stato locale corrente.
 * @param reason Motivo del blocco ricevuto dal coordinatore o dal backend.
 * @returns Copia bloccata; nessun retry, rebase o scarto automatico dei dati.
 * @throws AdminCardDraftError se i dati da clonare sono invalidi.
 */
export function blockAdminCardDraftSession(
	session: AdminCardDraftSession,
	reason: string
): AdminCardDraftSession {
	return {
		...copySession(session),
		blockedReason: reason || 'Modifiche bloccate dal backend'
	};
}

/**
 * Scarta esplicitamente i clic locali, conservando l'eventuale blocco corrente.
 * @param session Stato da ripristinare alla sua baseline, non riletto dal server.
 * @returns Nuova sessione senza operazioni; nessuna scrittura o lettura REST.
 * @throws AdminCardDraftError se la baseline e' invalida.
 * La conferma dell'utente prima dello scarto spetta alla futura integrazione UI.
 */
export function resetAdminCardDraftSession(session: AdminCardDraftSession): AdminCardDraftSession {
	const baseline = planAdminCardTransfers(session.baseline, []);
	return {
		baseline,
		preview: planAdminCardTransfers(baseline, []),
		transfers: [],
		blockedReason: session.blockedReason
	};
}
