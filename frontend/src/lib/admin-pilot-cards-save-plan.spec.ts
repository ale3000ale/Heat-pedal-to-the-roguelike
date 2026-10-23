import { describe, expect, it } from 'vitest';
import { AdminCardDraftError } from './admin-pilot-cards-draft';
import {
	appendAdminCardDraftTransfer,
	blockAdminCardDraftSession,
	createAdminCardDraftSession
} from './admin-pilot-cards-session';
import { prepareAdminCardSave } from './admin-pilot-cards-save-plan';
import type { AdminDeckRead, AdminPilotCardsRead } from './admin-pilot-cards-types';

const path = 'cards/turbo.webp';

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

function draft() {
	return appendAdminCardDraftTransfer(createAdminCardDraftSession(snapshot()), {
		source: 'game_deck',
		path
	});
}

describe('preparazione pura del salvataggio admin', () => {
	it('usa tutte le versioni iniziali e una riga per copia senza completare il mazzo', () => {
		const session = draft();
		const before = structuredClone(session);
		const plan = prepareAdminCardSave(session);
		expect(plan.request).toEqual({
			versions: {
				game_deck: { id: 1, version: 3 },
				modification_inventory: { id: 2, version: 3 },
				sponsor_inventory: { id: 3, version: 3 },
				modification_pool: { id: 4, version: 3 },
				sponsor_pool: { id: 5, version: 3 }
			},
			transfers: [{ source: 'game_deck', path }]
		});
		expect(plan.preview.containers.game_deck.cards[0].copies).toBe(1);
		expect(plan.preview.containers.modification_pool.cards[0].copies).toBe(3);
		expect(plan.summary).toEqual(['1 copia di "Turbo": Mazzo da gioco → Pool Modifiche.']);
		expect(session).toEqual(before);
	});

	it('non usa copie o versioni di una anteprima alterata', () => {
		const session = draft();
		session.preview.containers.game_deck.version = 99;
		session.preview.containers.game_deck.cards[0].copies = 900;
		const before = structuredClone(session);
		const plan = prepareAdminCardSave(session);
		expect(plan.request.versions.game_deck.version).toBe(3);
		expect(plan.preview.containers.game_deck.cards[0].copies).toBe(1);
		expect(session).toEqual(before);
	});

	it('mantiene ordine e riepilogo anche per carte trasferite in un clic precedente', () => {
		const session = appendAdminCardDraftTransfer(draft(), { source: 'modification_pool', path });
		const plan = prepareAdminCardSave(session);
		expect(plan.request.transfers).toEqual(session.transfers);
		expect(plan.summary).toEqual([
			'1 copia di "Turbo": Mazzo da gioco → Pool Modifiche.',
			'1 copia di "Turbo": Pool Modifiche → Inventario Modifiche.'
		]);
		expect(plan.preview.containers.modification_inventory.cards[0].copies).toBe(3);
	});

	it('non condivide versioni, trasferimenti o carte con la sessione', () => {
		const session = draft();
		const before = structuredClone(session);
		const plan = prepareAdminCardSave(session);
		plan.request.versions.game_deck.version = 12;
		plan.request.transfers[0].path = 'cards/other.webp';
		plan.preview.containers.game_deck.cards[0].copies = 50;
		plan.summary.push('altra riga');
		expect(session).toEqual(before);
	});

	it('conserva pool assenti e registro vuoto senza inventare operazioni', () => {
		const source = snapshot();
		for (const name of ['modification_pool', 'sponsor_pool'] as const)
			source.containers[name] = { available: false, id: null, version: null, cards: [] };
		const plan = prepareAdminCardSave(createAdminCardDraftSession(source));
		expect(plan.request.versions.modification_pool).toBeNull();
		expect(plan.request.versions.sponsor_pool).toBeNull();
		expect(plan.request.transfers).toEqual([]);
		expect(plan.summary).toEqual([]);
		expect(plan.preview).toEqual(source);
	});

	it.each(['game_deck', 'modification_inventory', 'sponsor_inventory'] as const)(
		'rifiuta %s assente anche se non toccato',
		(name) => {
			const source = snapshot();
			source.containers[name] = { available: false, id: null, version: null, cards: [] };
			expect(() => {
				prepareAdminCardSave(createAdminCardDraftSession(source));
			}).toThrow(AdminCardDraftError);
		}
	);

	it.each([0, -1, 1.5, NaN, Infinity, Number.MAX_SAFE_INTEGER + 1, null])(
		'rifiuta versione %s senza mutare gli input',
		(version) => {
			const session = draft();
			session.baseline.containers.sponsor_inventory.version = version;
			const before = structuredClone(session);
			expect(() => {
				prepareAdminCardSave(session);
			}).toThrow(AdminCardDraftError);
			expect(session).toEqual(before);
		}
	);

	it.each([0, -1, 1.5, Number.MAX_SAFE_INTEGER + 1, null])('rifiuta ID %s della baseline', (id) => {
		const session = draft();
		session.baseline.containers.game_deck.id = id;
		expect(() => {
			prepareAdminCardSave(session);
		}).toThrow(AdminCardDraftError);
	});

	it.each(['id', 'version', 'cards'])(
		'non trasforma una pool assente con %s incoerente in null',
		(field) => {
			const source = snapshot();
			const pool: AdminDeckRead = { available: false, id: null, version: null, cards: [] };
			if (field === 'id') pool.id = 5;
			else if (field === 'version') pool.version = 3;
			else pool.cards = [{ name: 'Turbo', path, copies: 1 }];
			source.containers.sponsor_pool = pool;
			expect(() => {
				prepareAdminCardSave(createAdminCardDraftSession(source));
			}).toThrow(AdminCardDraftError);
		}
	);

	it('conserva la bozza quando e bloccata', () => {
		const session = blockAdminCardDraftSession(draft(), 'Conflitto');
		const before = structuredClone(session);
		expect(() => {
			prepareAdminCardSave(session);
		}).toThrow('Conflitto');
		expect(session).toEqual(before);
	});

	it('ricontrolla read_only della baseline anche senza blockedReason locale', () => {
		const session = draft();
		session.baseline.read_only = true;
		session.baseline.blocked_reason = 'Gara aperta';
		expect(() => {
			prepareAdminCardSave(session);
		}).toThrow('Gara aperta');
	});

	it('un errore tardivo non applica neppure il primo movimento agli input', () => {
		const session = draft();
		session.transfers.push({ source: 'game_deck', path: 'cards/missing.webp' });
		const before = structuredClone(session);
		expect(() => {
			prepareAdminCardSave(session);
		}).toThrow(AdminCardDraftError);
		expect(session).toEqual(before);
	});

	it('rifiuta una destinazione assente senza crearla', () => {
		const session = draft();
		session.baseline.containers.modification_pool = {
			available: false,
			id: null,
			version: null,
			cards: []
		};
		const before = structuredClone(session);
		expect(() => {
			prepareAdminCardSave(session);
		}).toThrow(AdminCardDraftError);
		expect(session).toEqual(before);
	});

	it.each(['', 'x'.repeat(256)])('rifiuta un percorso fuori contratto', (invalidPath) => {
		const session = draft();
		session.transfers[0].path = invalidPath;
		expect(() => {
			prepareAdminCardSave(session);
		}).toThrow(AdminCardDraftError);
	});

	it('conta i code point del percorso come il contratto Python', () => {
		const source = snapshot();
		const unicodePath = 'cards/' + '𐐀'.repeat(244) + '.webp';
		for (const deck of Object.values(source.containers)) deck.cards[0].path = unicodePath;
		const session = appendAdminCardDraftTransfer(createAdminCardDraftSession(source), {
			source: 'game_deck',
			path: unicodePath
		});
		expect(prepareAdminCardSave(session).request.transfers[0].path).toBe(unicodePath);
	});

	it('serializza solo source e path anche se il chiamante possiede campi extra', () => {
		const session = createAdminCardDraftSession(snapshot());
		const transfer = {
			source: 'game_deck' as const,
			path,
			destination: 'sponsor_pool',
			copies: 99
		};
		session.transfers = [transfer];
		const plan = prepareAdminCardSave(session);
		expect(plan.request.transfers).toEqual([{ source: 'game_deck', path }]);
		expect(plan.preview.containers.sponsor_pool.cards[0].copies).toBe(2);
	});
});
