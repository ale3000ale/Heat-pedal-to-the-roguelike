import { describe, expect, it } from 'vitest';
import { prepareAdminCardSave } from './admin-pilot-cards-save-plan';
import { appendAdminCardDraftTransfer, createAdminCardDraftSession } from './admin-pilot-cards-session';
import type { AdminCardContainerName } from './admin-pilot-cards-draft';
import type { AdminPilotCardsRead } from './admin-pilot-cards-types';

const path = 'cards/turbo.webp';
function snapshot(): AdminPilotCardsRead {
    const deck = (id: number) => ({ available: true, id, version: 3, cards: [{ name: 'Turbo', path, copies: 5 }] });
    return { championship_id: 7, pilot: { pilot_id: 11, name: 'Anna', user_id: 5, username: 'mario' }, read_only: false, blocked_reason: null, containers: { game_deck: deck(1), modification_inventory: deck(2), sponsor_inventory: deck(3), modification_pool: deck(4), sponsor_pool: deck(5) } };
}
function draft(sources: AdminCardContainerName[], source = snapshot()) {
    let session = createAdminCardDraftSession(source);
    for (const from of sources) session = appendAdminCardDraftTransfer(session, { source: from, path });
    return session;
}

describe('riepilogo effettivo del salvataggio admin', () => {
    it('accorpa copie ripetute lasciando intatto il registro PUT', () => {
        const session = draft(['game_deck', 'game_deck', 'game_deck']);
        const before = structuredClone(session);
        const plan = prepareAdminCardSave(session);
        expect(plan.summary).toEqual(['3 copie di "Turbo": Mazzo da gioco → Pool Modifiche.']);
        expect(plan.request.transfers).toEqual(session.transfers);
        expect(plan.request.transfers).toHaveLength(3);
        expect(plan.preview.containers.game_deck.cards[0].copies).toBe(2);
        expect(session).toEqual(before);
    });

    it.each([['modification_inventory', 'modification_pool'], ['sponsor_inventory', 'sponsor_pool']] as const)('compensa il giro %s/%s senza cancellare il registro', (from, back) => {
        const session = draft([from, back]);
        const plan = prepareAdminCardSave(session);
        expect(plan.summary).toEqual([]);
        expect(plan.preview).toEqual(session.baseline);
        expect(plan.request.transfers).toEqual(session.transfers);
        expect(plan.request.transfers).toHaveLength(2);
    });

    it('mostra solo la quantita residua dopo un ritorno parziale', () => {
        const session = draft(['modification_inventory', 'modification_inventory', 'modification_pool']);
        const plan = prepareAdminCardSave(session);
        expect(plan.summary).toEqual(['1 copia di "Turbo": Inventario Modifiche → Pool Modifiche.']);
        expect(plan.preview.containers.modification_inventory.cards[0].copies).toBe(4);
        expect(plan.preview.containers.modification_pool.cards[0].copies).toBe(6);
        expect(plan.request.transfers).toHaveLength(3);
    });

    it('non inventa un trasferimento diretto mazzo/inventario nel riepilogo', () => {
        const plan = prepareAdminCardSave(draft(['game_deck', 'modification_pool']));
        expect(plan.summary).toEqual(['1 copia di "Turbo": Mazzo da gioco → Pool Modifiche.', '1 copia di "Turbo": Pool Modifiche → Inventario Modifiche.']);
    });

    it('compensa lo stesso nome normalizzato senza alterare identita o immagini', () => {
        const source = snapshot();
        source.containers.modification_pool.cards[0].name = 'TURBO';
        const session = draft(['modification_inventory', 'modification_pool'], source);
        const before = structuredClone(session);
        expect(prepareAdminCardSave(session).summary).toEqual([]);
        expect(session).toEqual(before);
    });
});
