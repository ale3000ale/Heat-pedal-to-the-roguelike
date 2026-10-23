import { adminCardIdentity } from './admin-card-identity';
import type {
	AdminCardContainers,
	AdminDeckRead,
	AdminPilotCardsRead
} from './admin-pilot-cards-types';
import type { CardEntry } from './types';

export type AdminCardContainerName = keyof AdminCardContainers;

/** Un clic: la destinazione non e' scelta dal chiamante. */
export interface AdminCardTransfer {
	source: AdminCardContainerName;
	path: string;
}

const destinations: Record<AdminCardContainerName, AdminCardContainerName> = {
	game_deck: 'modification_pool',
	modification_inventory: 'modification_pool',
	sponsor_inventory: 'sponsor_pool',
	modification_pool: 'modification_inventory',
	sponsor_pool: 'sponsor_inventory'
};

export class AdminCardDraftError extends Error {
	constructor(message: string) {
		super(message);
		this.name = 'AdminCardDraftError';
	}
}

/** Clona e valida le carte di un contenitore, senza condividere righe modificabili. */
function cloneDeck(deck: AdminDeckRead): AdminDeckRead {
	const names = new Set<string>();
	const cards = deck.cards.map((card) => {
		if (
			typeof card.name !== 'string' ||
			Array.from(card.name).length < 1 ||
			Array.from(card.name).length > 64 ||
			typeof card.path !== 'string' ||
			Array.from(card.path).length < 1 ||
			Array.from(card.path).length > 255 ||
			!Number.isInteger(card.copies) ||
			card.copies < 1 ||
			card.copies > 999
		) {
			throw new AdminCardDraftError('Carte non valide o limite di copie superato');
		}
		const key = adminCardIdentity(card.name);
		if (names.has(key)) throw new AdminCardDraftError('Carta duplicata nello stesso contenitore');
		names.add(key);
		return { ...card };
	});
	return { ...deck, cards };
}

/** Sposta una copia nelle sole liste clonate; rifiuta immagini discordanti o ambiguita'. */
function moveOne(source: CardEntry[], target: CardEntry[], path: string): void {
	const matches = source.filter((card) => card.path === path);
	const card = matches[0];
	if (matches.length !== 1 || !card) {
		throw new AdminCardDraftError('Carta sorgente assente o percorso ambiguo');
	}
	const existing = target.find(
		(row) => adminCardIdentity(row.name) === adminCardIdentity(card.name)
	);
	if (existing) {
		if (existing.path !== card.path) {
			throw new AdminCardDraftError('Nome carta associato a immagini diverse');
		}
		if (existing.copies >= 999) {
			throw new AdminCardDraftError('Carte non valide o limite di copie superato');
		}
		existing.copies += 1;
	} else {
		target.push({ ...card, copies: 1 });
	}
	if (card.copies === 1) source.splice(source.indexOf(card), 1);
	else card.copies -= 1;
}

/**
 * Applica i clic in ordine a una copia indipendente dello snapshot iniziale.
 * @param snapshot Stato letto dal backend, inclusi blocchi e versioni.
 * @param transfers Operazioni locali; una copia per elemento.
 * @returns Nuovo snapshot di bozza; ID e versioni non vengono incrementati.
 * @throws AdminCardDraftError per blocco locale, carta, pool o movimento incompatibile.
 * Non muta gli input neppure su errore tardivo; non autorizza un futuro salvataggio.
 * Non esegue rete, eventi, retry, completamenti del mazzo o scritture persistenti.
 */
export function planAdminCardTransfers(
	snapshot: AdminPilotCardsRead,
	transfers: readonly AdminCardTransfer[]
): AdminPilotCardsRead {
	if (snapshot.read_only && transfers.length > 0) {
		throw new AdminCardDraftError(snapshot.blocked_reason ?? 'Modifiche bloccate dal backend');
	}
	const planned: AdminPilotCardsRead = {
		...snapshot,
		pilot: { ...snapshot.pilot },
		containers: {
			game_deck: cloneDeck(snapshot.containers.game_deck),
			modification_inventory: cloneDeck(snapshot.containers.modification_inventory),
			sponsor_inventory: cloneDeck(snapshot.containers.sponsor_inventory),
			modification_pool: cloneDeck(snapshot.containers.modification_pool),
			sponsor_pool: cloneDeck(snapshot.containers.sponsor_pool)
		}
	};
	for (const transfer of transfers) {
		if (!Object.hasOwn(destinations, transfer.source)) {
			throw new AdminCardDraftError('Contenitore sorgente non valido');
		}
		if (typeof transfer.path !== 'string' || transfer.path.length === 0) {
			throw new AdminCardDraftError('Percorso della carta non valido');
		}
		const source = planned.containers[transfer.source];
		const target = planned.containers[destinations[transfer.source]];
		if (!source.available || !target.available) {
			throw new AdminCardDraftError('Contenitore non disponibile');
		}
		moveOne(source.cards, target.cards, transfer.path);
	}
	return planned;
}
