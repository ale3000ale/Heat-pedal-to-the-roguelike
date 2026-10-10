from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.shop import PackTemplate, ShopTemplate, ShopTemplatePack
from app.services.names import clean_name, name_key
from app.services.pack_templates import PackTemplateNotFoundError


class ShopTemplateNotFoundError(Exception):
    """Il template di negozio non esiste."""


class ShopTemplateNameTakenError(Exception):
    """Esiste già un template di negozio con questo nome."""


class ShopTemplateEmptyError(Exception):
    """Un template di negozio nuovo deve contenere almeno un template di pacchetto."""


class DuplicatePackTemplateError(Exception):
    """Lo stesso template di pacchetto compare due volte nello stesso template di negozio."""


@dataclass
class ShopTemplateInfo:
    # Template di negozio con i template di pacchetto che usa.
    id: int
    name: str
    created_at: datetime
    pack_template_ids: list[int]

    @property
    def is_empty(self) -> bool:
        # Indicatore "vuoto" (triangolo giallo): calcolato, non salvato. Un template
        # vuoto non è utilizzabile nella creazione di un campionato.
        return not self.pack_template_ids


def _pack_ids(db: Session, shop_template_id: int) -> list[int]:
    stmt = (
        select(ShopTemplatePack.pack_template_id)
        .where(ShopTemplatePack.shop_template_id == shop_template_id)
        .order_by(ShopTemplatePack.pack_template_id)
    )
    return list(db.scalars(stmt))


def _info(db: Session, template: ShopTemplate) -> ShopTemplateInfo:
    return ShopTemplateInfo(
        id=template.id,
        name=template.name,
        created_at=template.created_at,
        pack_template_ids=_pack_ids(db, template.id),
    )


def _check_pack_templates(db: Session, pack_template_ids: list[int]) -> None:
    # Errori: DuplicatePackTemplateError se un id si ripete, PackTemplateNotFoundError se
    # un template di pacchetto non esiste.
    if len(set(pack_template_ids)) != len(pack_template_ids):
        raise DuplicatePackTemplateError
    for pack_template_id in pack_template_ids:
        if db.get(PackTemplate, pack_template_id) is None:
            raise PackTemplateNotFoundError


def _name_in_use(db: Session, key: str, ignore_id: int | None = None) -> bool:
    stmt = select(ShopTemplate.id).where(ShopTemplate.name_key == key)
    if ignore_id is not None:
        stmt = stmt.where(ShopTemplate.id != ignore_id)
    return db.scalar(stmt) is not None


def _replace_links(db: Session, shop_template_id: int, pack_template_ids: list[int]) -> None:
    # Sostituisce i collegamenti del template, senza commit.
    db.execute(
        delete(ShopTemplatePack).where(ShopTemplatePack.shop_template_id == shop_template_id)
    )
    for pack_template_id in pack_template_ids:
        db.add(
            ShopTemplatePack(
                shop_template_id=shop_template_id, pack_template_id=pack_template_id
            )
        )


def list_shop_templates(db: Session) -> list[ShopTemplateInfo]:
    # Tutti i template di negozio, in ordine alfabetico senza distinguere le maiuscole.
    stmt = select(ShopTemplate).order_by(func.lower(ShopTemplate.name), ShopTemplate.id)
    return [_info(db, template) for template in db.scalars(stmt)]


def get_shop_template(db: Session, shop_template_id: int) -> ShopTemplateInfo:
    template = db.get(ShopTemplate, shop_template_id)
    if template is None:
        raise ShopTemplateNotFoundError
    return _info(db, template)


def create_shop_template(
    db: Session, name: str, pack_template_ids: list[int]
) -> ShopTemplateInfo:
    # Crea un template di negozio collegato ai template di pacchetto indicati.
    # Errori: ShopTemplateEmptyError senza template di pacchetto, DuplicatePackTemplateError,
    # PackTemplateNotFoundError, ShopTemplateNameTakenError.
    if not pack_template_ids:
        raise ShopTemplateEmptyError
    _check_pack_templates(db, pack_template_ids)
    name = clean_name(name)
    key = name_key(name)
    if _name_in_use(db, key):
        raise ShopTemplateNameTakenError
    template = ShopTemplate(name=name, name_key=key)
    db.add(template)
    try:
        db.flush()
        _replace_links(db, template.id, pack_template_ids)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ShopTemplateNameTakenError
    return _info(db, template)


def update_shop_template(
    db: Session, shop_template_id: int, name: str, pack_template_ids: list[int]
) -> ShopTemplateInfo:
    # Rinomina il template e ne sostituisce i template di pacchetto. L'elenco può essere
    # vuoto (il template resta ma non è utilizzabile), come dopo l'eliminazione di tutti i
    # suoi template di pacchetto.
    # Errori: ShopTemplateNotFoundError, DuplicatePackTemplateError, PackTemplateNotFoundError,
    # ShopTemplateNameTakenError.
    template = db.get(ShopTemplate, shop_template_id)
    if template is None:
        raise ShopTemplateNotFoundError
    _check_pack_templates(db, pack_template_ids)
    name = clean_name(name)
    key = name_key(name)
    if _name_in_use(db, key, ignore_id=template.id):
        raise ShopTemplateNameTakenError
    template.name = name
    template.name_key = key
    try:
        _replace_links(db, template.id, pack_template_ids)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ShopTemplateNameTakenError
    return _info(db, template)


def delete_shop_template(db: Session, shop_template_id: int) -> None:
    # Elimina il template di negozio e i suoi collegamenti; i template di pacchetto e i
    # campionati già creati non cambiano.
    template = db.get(ShopTemplate, shop_template_id)
    if template is None:
        raise ShopTemplateNotFoundError
    db.execute(
        delete(ShopTemplatePack).where(ShopTemplatePack.shop_template_id == template.id)
    )
    db.delete(template)
    db.commit()
