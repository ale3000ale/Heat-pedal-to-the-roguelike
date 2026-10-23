import { describe, expect, it } from 'vitest';
import { adminCardIdentity } from './admin-card-identity';
import {
	AdminCardDraftError,
	planAdminCardTransfers,
	type AdminCardContainerName
} from './admin-pilot-cards-draft';
import type { AdminDeckRead, AdminPilotCardsRead } from './admin-pilot-cards-types';

const path = 'cards/turbo.webp';
const directions: [AdminCardContainerName, AdminCardContainerName][] = [
	['game_deck', 'modification_pool'],
	['modification_inventory', 'modification_pool'],
	['sponsor_inventory', 'sponsor_pool'],
	['modification_pool', 'modification_inventory'],
	['sponsor_pool', 'sponsor_inventory']
];

function snapshot(): AdminPilotCardsRead {
	const deck = (id: number): AdminDeckRead => ({
		available: true,
		id,
		version: 4,
		cards: [{ name: 'Turbo', path, copies: 2 }]
	});
	return {
		championship_id: 7,
		pilot: { pilot_id: 11, name: 'Anna', user_id: 5, username: 'mario' },
		read_only: false,
		blocked_reason: null,
		containers: {
			game_deck: deck(1),
			modification_inventory: deck(2),
			sponsor_inventory: deck(3),
			modification_pool: deck(4),
			sponsor_pool: deck(5)
		}
	};
}

function copies(deck: AdminDeckRead): number {
	return deck.cards.reduce((sum, card) => sum + card.copies, 0);
}

describe('bozza dei trasferimenti admin', () => {
	it.each(directions)('sposta una sola copia da %s a %s', (source, target) => {
		const original = snapshot();
		const before = structuredClone(original);
		const result = planAdminCardTransfers(original, [{ source, path }]);
		for (const key of Object.keys(original.containers) as AdminCardContainerName[]) {
			const expected = key === source ? 1 : key === target ? 3 : 2;
			expect(copies(result.containers[key])).toBe(expected);
			expect(result.containers[key].id).toBe(before.containers[key].id);
			expect(result.containers[key].version).toBe(4);
		}
		expect(Object.values(result.containers).reduce((sum, deck) => sum + copies(deck), 0)).toBe(10);
		expect(original).toEqual(before);
	});

	it('clona anche i contenitori e le carte non toccati', () => {
		const original = snapshot();
		const result = planAdminCardTransfers(original, []);
		expect(result).toEqual(original);
		expect(result.pilot).not.toBe(original.pilot);
		for (const key of Object.keys(original.containers) as AdminCardContainerName[]) {
			expect(result.containers[key]).not.toBe(original.containers[key]);
			expect(result.containers[key].cards).not.toBe(original.containers[key].cards);
			expect(result.containers[key].cards[0]).not.toBe(original.containers[key].cards[0]);
		}
	});

	it('rimuove la riga a zero e non applica parzialmente una sequenza fallita', () => {
		const original = snapshot();
		const before = structuredClone(original);
		const clicks = [
			{ source: 'game_deck' as const, path },
			{ source: 'game_deck' as const, path }
		];
		expect(planAdminCardTransfers(original, clicks).containers.game_deck.cards).toEqual([]);
		expect(() => {
			planAdminCardTransfers(original, [...clicks, clicks[0]]);
		}).toThrow(AdminCardDraftError);
		expect(original).toEqual(before);
	});

	it.each(directions)('non crea la destinazione assente per un clic da %s', (source, target) => {
		const original = snapshot();
		original.containers[target] = { available: false, id: null, version: null, cards: [] };
		const before = structuredClone(original);
		expect(() => {
			planAdminCardTransfers(original, [{ source, path }]);
		}).toThrow('Contenitore non disponibile');
		expect(original).toEqual(before);
	});

	it('rifiuta una sorgente assente e il blocco autorevole dello snapshot', () => {
		const original = snapshot();
		original.containers.sponsor_pool = {
			available: false,
			id: null,
			version: null,
			cards: []
		};
		expect(() => {
			planAdminCardTransfers(original, [{ source: 'sponsor_pool', path }]);
		}).toThrow(AdminCardDraftError);
		original.read_only = true;
		original.blocked_reason = 'Gara o revisione non ancora confermata';
		expect(() => {
			planAdminCardTransfers(original, [{ source: 'game_deck', path }]);
		}).toThrow(original.blocked_reason);
	});

	it.each(['assente', 'ambiguo'])('rifiuta il percorso sorgente %s', (kind) => {
		const original = snapshot();
		if (kind === 'ambiguo') {
			original.containers.game_deck.cards.push({ name: 'Altro', path, copies: 1 });
		}
		const before = structuredClone(original);
		const selected = kind === 'assente' ? 'cards/missing.webp' : path;
		expect(() => {
			planAdminCardTransfers(original, [{ source: 'game_deck', path: selected }]);
		}).toThrow('Carta sorgente assente o percorso ambiguo');
		expect(original).toEqual(before);
	});

	it('conserva il nome esistente e rifiuta immagini discordanti', () => {
		const original = snapshot();
		original.containers.modification_pool.cards[0].name = ' TURBO ';
		const result = planAdminCardTransfers(original, [{ source: 'game_deck', path }]);
		expect(result.containers.modification_pool.cards[0]).toEqual({
			name: ' TURBO ',
			path,
			copies: 3
		});
		original.containers.modification_pool.cards[0].path = 'cards/other.webp';
		expect(() => {
			planAdminCardTransfers(original, [{ source: 'game_deck', path }]);
		}).toThrow('Nome carta associato a immagini diverse');
	});

	it('aggiunge una riga nuova senza sostituire immagini o completare il mazzo', () => {
		const original = snapshot();
		original.containers.modification_pool.cards = [];
		const result = planAdminCardTransfers(original, [{ source: 'game_deck', path }]);
		expect(result.containers.modification_pool.cards).toEqual([{ name: 'Turbo', path, copies: 1 }]);
		expect(copies(result.containers.game_deck)).toBe(1);
		expect(copies(result.containers.modification_inventory)).toBe(2);
	});

	it('rifiuta duplicati per identita Unicode, copie non valide e overflow', () => {
		const duplicate = snapshot();
		duplicate.containers.game_deck.cards = [
			{ name: 'Straße', path, copies: 1 },
			{ name: 'STRASSE', path: 'cards/b.webp', copies: 1 }
		];
		expect(() => {
			planAdminCardTransfers(duplicate, []);
		}).toThrow(AdminCardDraftError);
		const invalid = snapshot();
		invalid.containers.game_deck.cards[0].copies = 0;
		expect(() => {
			planAdminCardTransfers(invalid, []);
		}).toThrow(AdminCardDraftError);
		const overflow = snapshot();
		overflow.containers.modification_pool.cards[0].copies = 999;
		const before = structuredClone(overflow);
		expect(() => {
			planAdminCardTransfers(overflow, [{ source: 'game_deck', path }]);
		}).toThrow(AdminCardDraftError);
		expect(overflow).toEqual(before);
	});

	it('rifiuta sorgenti arbitrarie senza usare proprieta ereditate', () => {
		expect(() => {
			planAdminCardTransfers(snapshot(), [{ source: 'constructor' as AdminCardContainerName, path }]);
		}).toThrow('Contenitore sorgente non valido');
	});
});

describe('identita coerente con strip e casefold Python', () => {
	it.each([
		[' STRAẞE ', 'strasse'],
		['ΟΣ', 'οσ'],
		['ος', 'οσ'],
		['ﬃ', 'ffi'],
		['Ꭰꭰ', 'ᎠᎠ'],
		['\u001cTurbo\u0085', 'turbo'],
		['\uFEFFX\uFEFF', '\uFEFFx\uFEFF']
	])('confronta %s come %s', (name, expected) => {
		expect(adminCardIdentity(name)).toBe(expected);
	});

	it('non aggiunge una normalizzazione Unicode o la rimozione degli accenti', () => {
		expect(adminCardIdentity('É')).toBe('é');
		expect(adminCardIdentity('É')).not.toBe(adminCardIdentity('e\u0301'));
	});
});
