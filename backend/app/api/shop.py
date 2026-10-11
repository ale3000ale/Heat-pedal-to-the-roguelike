from fastapi import APIRouter, HTTPException, Query, Request, status

from app.api.deps import AdminUser, DbDep
from app.schemas.shop import (
    PackData,
    PackImageRead,
    PackTemplateRead,
    ShopTemplateData,
    ShopTemplateRead,
)
from app.services.pack_images import (
    MAX_UPLOAD_BYTES,
    PackImageError,
    list_pack_images,
    save_pack_image,
)
from app.services.pack_templates import (
    PackTemplateNotFoundError,
    create_pack_template,
    delete_pack_template,
    get_pack_template,
    list_pack_templates,
    update_pack_template,
)
from app.services.shop_templates import (
    DuplicatePackTemplateError,
    ShopTemplateEmptyError,
    ShopTemplateInfo,
    ShopTemplateNameTakenError,
    ShopTemplateNotFoundError,
    create_shop_template,
    delete_shop_template,
    get_shop_template,
    list_shop_templates,
    update_shop_template,
)

router = APIRouter(tags=["shop"])

TEMPLATE_NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Template di pacchetto non trovato")
SHOP_TEMPLATE_NOT_FOUND = HTTPException(
    status.HTTP_404_NOT_FOUND, "Template di negozio non trovato"
)


def _shop_read(info: ShopTemplateInfo) -> ShopTemplateRead:
    return ShopTemplateRead(
        id=info.id,
        name=info.name,
        created_at=info.created_at,
        pack_template_ids=info.pack_template_ids,
        is_empty=info.is_empty,
    )


@router.get("/pack-templates", response_model=list[PackTemplateRead])
def list_templates(admin: AdminUser, db: DbDep):
    # Tutti i template di pacchetto (solo admin).
    return list_pack_templates(db)


@router.post(
    "/pack-templates", response_model=PackTemplateRead, status_code=status.HTTP_201_CREATED
)
def create_template(data: PackData, admin: AdminUser, db: DbDep):
    # Crea un template di pacchetto (solo admin); 422 se l'immagine non è disponibile.
    try:
        return create_pack_template(db, data.model_dump())
    except PackImageError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc))


@router.get("/pack-templates/{template_id}", response_model=PackTemplateRead)
def read_template(template_id: int, admin: AdminUser, db: DbDep):
    try:
        return get_pack_template(db, template_id)
    except PackTemplateNotFoundError:
        raise TEMPLATE_NOT_FOUND


@router.put("/pack-templates/{template_id}", response_model=PackTemplateRead)
def change_template(template_id: int, data: PackData, admin: AdminUser, db: DbDep):
    # Modifica per intero un template (solo admin); 404 se non esiste, 422 se l'immagine
    # non è disponibile.
    try:
        return update_pack_template(db, template_id, data.model_dump())
    except PackTemplateNotFoundError:
        raise TEMPLATE_NOT_FOUND
    except PackImageError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc))


@router.delete("/pack-templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_template(template_id: int, admin: AdminUser, db: DbDep):
    # Elimina un template (solo admin) e lo toglie dai template di negozio.
    try:
        delete_pack_template(db, template_id)
    except PackTemplateNotFoundError:
        raise TEMPLATE_NOT_FOUND


@router.get("/shop-templates", response_model=list[ShopTemplateRead])
def list_shop_template_rows(admin: AdminUser, db: DbDep):
    # Tutti i template di negozio, con l'indicatore "vuoto" (solo admin).
    return [_shop_read(info) for info in list_shop_templates(db)]


@router.post(
    "/shop-templates", response_model=ShopTemplateRead, status_code=status.HTTP_201_CREATED
)
def create_shop_template_row(data: ShopTemplateData, admin: AdminUser, db: DbDep):
    # Crea un template di negozio (solo admin). 404 se un template di pacchetto non esiste,
    # 409 se il nome è in uso, 422 se non ha template di pacchetto o ne ripete uno.
    try:
        return _shop_read(create_shop_template(db, data.name, data.pack_template_ids))
    except ShopTemplateEmptyError:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "Servono almeno un template di pacchetto",
        )
    except DuplicatePackTemplateError:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "Template di pacchetto ripetuto"
        )
    except PackTemplateNotFoundError:
        raise TEMPLATE_NOT_FOUND
    except ShopTemplateNameTakenError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Nome già in uso")


@router.get("/shop-templates/{shop_template_id}", response_model=ShopTemplateRead)
def read_shop_template(shop_template_id: int, admin: AdminUser, db: DbDep):
    try:
        return _shop_read(get_shop_template(db, shop_template_id))
    except ShopTemplateNotFoundError:
        raise SHOP_TEMPLATE_NOT_FOUND


@router.put("/shop-templates/{shop_template_id}", response_model=ShopTemplateRead)
def change_shop_template(
    shop_template_id: int, data: ShopTemplateData, admin: AdminUser, db: DbDep
):
    # Rinomina un template di negozio e ne sostituisce i template di pacchetto (solo
    # admin); l'elenco può essere vuoto.
    try:
        return _shop_read(
            update_shop_template(db, shop_template_id, data.name, data.pack_template_ids)
        )
    except ShopTemplateNotFoundError:
        raise SHOP_TEMPLATE_NOT_FOUND
    except DuplicatePackTemplateError:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "Template di pacchetto ripetuto"
        )
    except PackTemplateNotFoundError:
        raise TEMPLATE_NOT_FOUND
    except ShopTemplateNameTakenError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Nome già in uso")


@router.delete("/shop-templates/{shop_template_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_shop_template(shop_template_id: int, admin: AdminUser, db: DbDep):
    # Elimina un template di negozio (solo admin); i template di pacchetto restano.
    try:
        delete_shop_template(db, shop_template_id)
    except ShopTemplateNotFoundError:
        raise SHOP_TEMPLATE_NOT_FOUND


@router.get("/images", response_model=list[PackImageRead])
def list_images(admin: AdminUser):
    # Immagini disponibili per i pacchetti (solo admin). Il file si legge da
    # /media/pack/<path>.
    return [PackImageRead(path=path) for path in list_pack_images()]


@router.post("/images", response_model=PackImageRead, status_code=status.HTTP_201_CREATED)
async def upload_image(
    request: Request,
    admin: AdminUser,
    filename: str = Query(min_length=1, max_length=120),
):
    # Carica un'immagine (solo admin): il corpo della richiesta è il file stesso e il
    # nome arriva nel parametro filename. 413 se supera 5 MB, 422 se non è valida.
    declared = request.headers.get("content-length")
    if declared is not None and declared.isdigit() and int(declared) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File troppo grande (massimo 5 MB)")
    data = await request.body()
    try:
        return PackImageRead(path=save_pack_image(filename, data))
    except PackImageError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc))
