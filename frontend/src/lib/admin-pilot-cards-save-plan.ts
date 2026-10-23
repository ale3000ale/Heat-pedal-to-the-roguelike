import {
	AdminCardDraftError,
	planAdminCardTransfers,
	type AdminCardContainerName
} from './admin-pilot-cards-draft';
import type { AdminCardDraftSession } from './admin-pilot-cards-session';
import type { AdminExpectedDeckVersion, AdminPilotCardsSave } from './admin-pilot-cards-save-types';
import type { AdminDeckRead, AdminPilotCardsRead } from './admin-pilot-cards-types';

export interface AdminCardSavePlan {
	request: AdminPilotCardsSave;
	preview: AdminPilotCardsRead;
	summary: string[];
}

// Etichette del riepilogo: non decidono gli spostamenti, applicati dal pianificatore.
const directions: Record<AdminCardContainerName, string> = {
	game_deck: 'Mazzo da gioco → Pool Modifiche',
	modification_inventory: 'Inventario Modifiche → Pool Modifiche',
	sponsor_inventory: 'Inventario Sponsor → Pool Sponsor',
	modification_pool: 'Pool Modifiche → Inventario Modifiche',
	sponsor_pool: 'Pool Sponsor → Inventario Sponsor'
};

/**
 * Estrae una coppia originale rappresentabile senza arrotondamenti JavaScript.
 * @param deck Contenitore presente nella baseline.
 * @returns Nuovo oggetto con soli id e version.
 * @throws AdminCardDraftError per contenitore assente o coppia non valida.
 */
function expectedVersion(deck: AdminDeckRead): AdminExpectedDeckVersion {
	if (!deck.available) throw new AdminCardDraftError('Contenitore obbligatorio non disponibile');
	const { id, version } = deck;
	if (
		typeof id !== 'number' ||
		!Number.isSafeInteger(id) ||
		id <= 0 ||
		typeof version !== 'number' ||
		!Number.isSafeInteger(version) ||
		version <= 0
	) {
		throw new AdminCardDraftError('ID o versione della baseline non validi');
	}
	return { id, version };
}

/**
 * Conserva null per una pool realmente assente, senza inventare ID o versioni.
 * @param deck Pool della baseline.
 * @returns Coppia attesa oppure null.
 * @throws AdminCardDraftError per disponibilita' e metadati incoerenti.
 */
function expectedPoolVersion(deck: AdminDeckRead): AdminExpectedDeckVersion | null {
	if (deck.available) return expectedVersion(deck);
	if (deck.id !== null || deck.version !== null || deck.cards.length !== 0) {
		throw new AdminCardDraftError('Pool assente con dati incoerenti');
	}
	return null;
}

/**
 * Prepara richiesta e riepilogo dalla stessa sequenza, senza rete o scritture.
 * @param session Bozza corrente; baseline, anteprima e registro non vengono mutati.
 * @returns Richiesta indipendente, anteprima ricalcolata e una riga per clic in ordine.
 * @throws AdminCardDraftError su blocco, versioni, percorsi o movimenti invalidi.
 * Ignora l'anteprima memorizzata e usa le versioni di tutti i contenitori iniziali.
 * Un errore tardivo non applica parzialmente nulla alla sessione. Il riepilogo
 * descrive operazioni, non differenze nette; un registro vuoto resta vuoto.
 */
export function prepareAdminCardSave(session: AdminCardDraftSession): AdminCardSavePlan {
	if (session.blockedReason !== null || session.baseline.read_only) {
		throw new AdminCardDraftError(
			session.blockedReason ?? session.baseline.blocked_reason ?? 'Modifiche bloccate dal backend'
		);
	}
	let preview = planAdminCardTransfers(session.baseline, []);
	const decks = preview.containers;
	const versions = {
		game_deck: expectedVersion(decks.game_deck),
		modification_inventory: expectedVersion(decks.modification_inventory),
		sponsor_inventory: expectedVersion(decks.sponsor_inventory),
		modification_pool: expectedPoolVersion(decks.modification_pool),
		sponsor_pool: expectedPoolVersion(decks.sponsor_pool)
	};
	const transfers = session.transfers.map(({ source, path }) => ({ source, path }));
	const summary: string[] = [];
	for (const transfer of transfers) {
		if (
			typeof transfer.path !== 'string' ||
			Array.from(transfer.path).length < 1 ||
			Array.from(transfer.path).length > 255
		) {
			throw new AdminCardDraftError('Percorso della carta non valido');
		}
		// Il dominio valida anche la sorgente prima che venga usata per il riepilogo.
		const next = planAdminCardTransfers(preview, [transfer]);
		const card = preview.containers[transfer.source].cards.find(
			(row) => row.path === transfer.path
		);
		if (!card) throw new AdminCardDraftError('Carta sorgente assente nel riepilogo');
		summary.push(`1 copia di "${card.name}": ${directions[transfer.source]}.`);
		preview = next;
	}
	return { request: { versions, transfers }, preview, summary };
}
