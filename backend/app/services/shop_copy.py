from sqlalchemy.orm import Session

from app.db.models.shop import Pack, PackTemplate
from app.services.pack_values import apply_pack_values, values_of
from app.services.shop_templates import ShopTemplateEmptyError, get_shop_template


def pack_templates_of(db: Session, shop_template_id: int) -> list[PackTemplate]:
    # I template di pacchetto collegati a un template di negozio utilizzabile.
    # Errori: ShopTemplateNotFoundError se non esiste, ShopTemplateEmptyError se non ha
    # template di pacchetto (non è utilizzabile).
    info = get_shop_template(db, shop_template_id)
    if info.is_empty:
        raise ShopTemplateEmptyError
    return [db.get(PackTemplate, pack_id) for pack_id in info.pack_template_ids]


def add_packs_from_templates(
    db: Session, championship_id: int, pack_templates: list[PackTemplate]
) -> list[Pack]:
    # Crea nel campionato una copia indipendente di ogni template di pacchetto: cambiare
    # o eliminare i template dopo non tocca questi pacchetti. Senza commit.
    packs = []
    for template in pack_templates:
        pack = Pack(championship_id=championship_id)
        apply_pack_values(pack, values_of(template))
        db.add(pack)
        packs.append(pack)
    return packs
