import { adminCardIdentity } from './admin-card-identity';
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
interface SummaryMovement {
	source: AdminCardContainerName;
	name: string;
	path: string;
}
const directions: Record<AdminCardContainerName, string> = {
	game_deck: 'Mazzo da gioco → Pool Modifiche',
	modification_inventory: 'Inventario Modifiche → Pool Modifiche',
	sponsor_inventory: 'Inventario Sponsor → Pool Sponsor',
	modification_pool: 'Pool Modifiche → Inventario Modifiche',
	sponsor_pool: 'Pool Sponsor → Inventario Sponsor'
};
const opposites: Partial<Record<AdminCardContainerName, AdminCardContainerName>> = {
	modification_inventory: 'modification_pool',
	modification_pool: 'modification_inventory',
	sponsor_inventory: 'sponsor_pool',
	sponsor_pool: 'sponsor_inventory'
};

/**
 * Accorpa copie della stessa carta e compensa soltanto i versi opposti approvati.
 * @param movements Movimenti gia' validati, una copia per elemento.
 * @returns Righe testuali delle variazioni residue, senza immagini o nuove destinazioni.
 * Non cambia l'ordine del registro PUT. Mazzo/pool non ha un verso inverso ammesso.
 */
function effectiveSummary(movements: readonly SummaryMovement[]): string[] {
	const rows = new Map<string, SummaryMovement & { copies: number }>();
	const key = (source: AdminCardContainerName, movement: SummaryMovement) =>
		JSON.stringify([source, adminCardIdentity(movement.name), movement.path]);
	for (const movement of movements) {
		const opposite = opposites[movement.source];
		const reverse = opposite ? rows.get(key(opposite, movement)) : undefined;
		if (reverse && reverse.copies > 0) {
			reverse.copies -= 1;
			continue;
		}
		const id = key(movement.source, movement);
		const existing = rows.get(id);
		if (existing) existing.copies += 1;
		else rows.set(id, { ...movement, copies: 1 });
	}
	return [...rows.values()]
		.filter((row) => row.copies > 0)
		.map(
			(row) =>
				`${row.copies} ${row.copies === 1 ? 'copia' : 'copie'} di "${row.name}": ${directions[row.source]}.`
		);
}

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
	)
		throw new AdminCardDraftError('ID o versione della baseline non validi');
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
	if (deck.id !== null || deck.version !== null || deck.cards.length !== 0)
		throw new AdminCardDraftError('Pool assente con dati incoerenti');
	return null;
}

/**
 * Prepara richiesta e riepilogo dalla stessa sequenza, senza rete o scritture.
 * @param session Bozza corrente; baseline, anteprima e registro non vengono mutati.
 * @returns Richiesta originale indipendente, anteprima ricalcolata e riepilogo effettivo.
 * @throws AdminCardDraftError su blocco, versioni, percorsi o movimenti invalidi.
 * Il backend riceve tutti i clic validati nel loro ordine; la sola presentazione
 * accorpa copie e compensa i versi opposti. Un errore tardivo non muta gli input.
 */
export function prepareAdminCardSave(session: AdminCardDraftSession): AdminCardSavePlan {
	if (session.blockedReason !== null || session.baseline.read_only)
		throw new AdminCardDraftError(
			session.blockedReason ?? session.baseline.blocked_reason ?? 'Modifiche bloccate dal backend'
		);
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
	const movements: SummaryMovement[] = [];
	for (const transfer of transfers) {
		if (
			typeof transfer.path !== 'string' ||
			Array.from(transfer.path).length < 1 ||
			Array.from(transfer.path).length > 255
		)
			throw new AdminCardDraftError('Percorso della carta non valido');
		const next = planAdminCardTransfers(preview, [transfer]);
		const card = preview.containers[transfer.source].cards.find(
			(row) => row.path === transfer.path
		);
		if (!card) throw new AdminCardDraftError('Carta sorgente assente nel riepilogo');
		movements.push({ source: transfer.source, path: card.path, name: card.name });
		preview = next;
	}
	return { request: { versions, transfers }, preview, summary: effectiveSummary(movements) };
}
