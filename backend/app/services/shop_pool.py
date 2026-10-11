from sqlalchemy.orm import Session

from app.schemas.shop_pool import ShopPoolCard, ShopPoolRead, ShopPoolSection
from app.services.cards import CardEntry
from app.services.championships import get_championship
from app.services.shop_view import load_pool


def pool_section(cards: list[CardEntry]) -> ShopPoolSection:
    # Riga per ogni carta con le copie rimaste e la probabilità percentuale alla prima
    # estrazione: copie della carta diviso copie totali, come in shop_draw (senza filtro).
    # Le carte sono ordinate dalla più probabile e, a parità, per nome.
    total = sum(card.copies for card in cards)
    ordered = sorted(cards, key=lambda card: (-card.copies, card.name.casefold()))
    rows = [
        ShopPoolCard(
            name=card.name,
            path=card.path,
            copies=card.copies,
            probability=round(card.copies / total * 100, 2) if total else 0.0,
        )
        for card in ordered
    ]
    return ShopPoolSection(total_copies=total, cards=rows)


def build_shop_pool(db: Session, championship_id: int) -> ShopPoolRead:
    # Pool delle modifiche e degli sponsor del campionato nello stato attuale.
    # Errori: ChampionshipNotFoundError se il campionato non esiste.
    championship = get_championship(db, championship_id)
    return ShopPoolRead(
        modifiche=pool_section(load_pool(db, championship.pool_deck_id)),
        sponsor=pool_section(load_pool(db, championship.sponsor_pool_deck_id)),
    )
