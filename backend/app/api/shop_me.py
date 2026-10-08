from fastapi import APIRouter

from app.api.deps import CurrentUser, DbDep
from app.schemas.shop_list import MyShopsRead, ShopEntryRead, ShopPilotRef
from app.services.shop_list import list_my_shops

router = APIRouter(tags=["shop-me"])


@router.get("/shops", response_model=MyShopsRead)
def read_my_shops(user: CurrentUser, db: DbDep):
    # Campionati attivi a cui l'utente partecipa con un pilota, con i piloti iscritti.
    # Serve alla voce "Negozio" della barra di navigazione e alla scelta del pilota.
    return MyShopsRead(
        shops=[
            ShopEntryRead(
                championship_id=entry.championship_id,
                championship_name=entry.championship_name,
                pilots=[ShopPilotRef(id=pilot.id, name=pilot.name) for pilot in entry.pilots],
            )
            for entry in list_my_shops(db, user)
        ]
    )
