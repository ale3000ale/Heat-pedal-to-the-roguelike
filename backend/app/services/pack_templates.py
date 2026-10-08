from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.db.models.shop import PackTemplate, ShopTemplatePack
from app.services.pack_values import apply_pack_values, resolve_image


class PackTemplateNotFoundError(Exception):
    """Il template di pacchetto non esiste."""


def list_pack_templates(db: Session) -> list[PackTemplate]:
    # Tutti i template di pacchetto, in ordine alfabetico senza distinguere le maiuscole.
    stmt = select(PackTemplate).order_by(func.lower(PackTemplate.name), PackTemplate.id)
    return list(db.scalars(stmt))


def get_pack_template(db: Session, template_id: int) -> PackTemplate:
    template = db.get(PackTemplate, template_id)
    if template is None:
        raise PackTemplateNotFoundError
    return template


def create_pack_template(db: Session, values: dict) -> PackTemplate:
    # Crea un template di pacchetto. Senza immagine usa quella predefinita.
    # Errori: PackImageError se l'immagine non è disponibile.
    values = {**values, "image_path": resolve_image(values.get("image_path"))}
    template = PackTemplate()
    apply_pack_values(template, values)
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def update_pack_template(db: Session, template_id: int, values: dict) -> PackTemplate:
    # Modifica per intero un template di pacchetto. La modifica si vede subito in tutti
    # i template di negozio che lo usano; i pacchetti dei campionati non cambiano.
    # Errori: PackTemplateNotFoundError, PackImageError se l'immagine non è disponibile.
    template = get_pack_template(db, template_id)
    values = {**values, "image_path": resolve_image(values.get("image_path"))}
    apply_pack_values(template, values)
    db.commit()
    db.refresh(template)
    return template


def delete_pack_template(db: Session, template_id: int) -> None:
    # Elimina il template e lo toglie da tutti i template di negozio che lo usano (i
    # template di negozio restano). Campionati e pacchetti già creati non cambiano.
    template = get_pack_template(db, template_id)
    db.execute(delete(ShopTemplatePack).where(ShopTemplatePack.pack_template_id == template.id))
    db.delete(template)
    db.commit()
