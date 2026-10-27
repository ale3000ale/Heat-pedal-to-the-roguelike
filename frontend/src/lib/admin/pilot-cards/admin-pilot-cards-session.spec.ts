import { describe, expect, it } from 'vitest';
import { AdminCardDraftError, type AdminCardTransfer } from './admin-pilot-cards-draft';
import {
	appendAdminCardDraftTransfer,
	blockAdminCardDraftSession,
	createAdminCardDraftSession,
	resetAdminCardDraftSession
} from './admin-pilot-cards-session';
import type { AdminDeckRead, AdminPilotCardsRead } from './admin-pilot-cards-types';

const path = 'cards/turbo.webp';
const transfer: AdminCardTransfer = { source: 'game_deck', path };

function snapshot(): AdminPilotCardsRead {
	const deck = (id: number): AdminDeckRead => ({
		available: true,
		id,
		version: 3,
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

describe('sessione locale della bozza carte admin', () => {
	it('separa snapshot ricevuto, baseline e anteprima', () => {
		const source = snapshot();
		const before = structuredClone(source);
		const session = createAdminCardDraftSession(source);
		expect(session.baseline).toEqual(source);
		expect(session.preview).toEqual(source);
		expect(session.transfers).toEqual([]);
		expect(session.blockedReason).toBeNull();
		session.preview.containers.game_deck.cards[0].copies = 1;
		expect(session.baseline.containers.game_deck.cards[0].copies).toBe(2);
		expect(source).toEqual(before);
	});

	it('aggiunge un clic senza cambiare la sessione precedente o le versioni', () => {
		const session = createAdminCardDraftSession(snapshot());
		const before = structuredClone(session);
		const next = appendAdminCardDraftTransfer(session, transfer);
		expect(next.transfers).toEqual([transfer]);
		expect(next.preview.containers.game_deck.cards[0].copies).toBe(1);
		expect(next.preview.containers.modification_pool.cards[0].copies).toBe(3);
		expect(next.preview.containers.modification_inventory.cards[0].copies).toBe(2);
		expect(next.baseline).toEqual(before.baseline);
		expect(next.preview.containers.game_deck.version).toBe(3);
		expect(session).toEqual(before);
	});

	it('ricalcola dalla baseline e dal registro, non da una vista alterata', () => {
		const session = createAdminCardDraftSession(snapshot());
		session.preview.containers.game_deck.cards[0].copies = 900;
		const next = appendAdminCardDraftTransfer(session, transfer);
		expect(next.preview.containers.game_deck.cards[0].copies).toBe(1);
	});

	it('un clic fallito conserva tutta la bozza gia preparata', () => {
		const first = appendAdminCardDraftTransfer(createAdminCardDraftSession(snapshot()), transfer);
		const second = appendAdminCardDraftTransfer(first, transfer);
		const before = structuredClone(second);
		expect(second.preview.containers.game_deck.cards).toEqual([]);
		expect(() => {
			appendAdminCardDraftTransfer(second, transfer);
		}).toThrow(AdminCardDraftError);
		expect(second).toEqual(before);
	});

	it('un blocco conserva anteprima e clic senza mutare la sessione precedente', () => {
		const session = appendAdminCardDraftTransfer(createAdminCardDraftSession(snapshot()), transfer);
		const before = structuredClone(session);
		const blocked = blockAdminCardDraftSession(session, 'Gara aperta');
		expect(blocked.preview).toEqual(before.preview);
		expect(blocked.transfers).toEqual(before.transfers);
		expect(blocked.baseline).toEqual(before.baseline);
		expect(() => {
			appendAdminCardDraftTransfer(blocked, transfer);
		}).toThrow('Gara aperta');
		expect(session).toEqual(before);
	});

	it('il ripristino esplicito conserva il blocco e non altera la vecchia bozza', () => {
		const session = appendAdminCardDraftTransfer(createAdminCardDraftSession(snapshot()), transfer);
		const blocked = blockAdminCardDraftSession(session, 'Conflitto');
		const before = structuredClone(blocked);
		const reset = resetAdminCardDraftSession(blocked);
		expect(reset.preview).toEqual(reset.baseline);
		expect(reset.transfers).toEqual([]);
		expect(reset.blockedReason).toBe('Conflitto');
		expect(blocked).toEqual(before);
	});

	it('mantiene il blocco iniziale restituito dal backend', () => {
		const source = snapshot();
		source.read_only = true;
		source.blocked_reason = 'Campionato chiuso';
		const session = createAdminCardDraftSession(source);
		expect(() => {
			appendAdminCardDraftTransfer(session, transfer);
		}).toThrow('Campionato chiuso');
		expect(resetAdminCardDraftSession(session).blockedReason).toBe('Campionato chiuso');
	});

	it('non condivide gli oggetti del registro tra chiamante e nuove sessioni', () => {
		const input: AdminCardTransfer = { ...transfer };
		const first = appendAdminCardDraftTransfer(createAdminCardDraftSession(snapshot()), input);
		input.path = 'cards/changed.webp';
		expect(first.transfers[0].path).toBe(path);
		const second = appendAdminCardDraftTransfer(first, transfer);
		second.transfers[0].path = 'cards/other.webp';
		expect(first.transfers[0].path).toBe(path);
	});
});
