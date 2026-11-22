"""Indirizzo del sito e QR per aprire Heat da un altro dispositivo."""
import os
from typing import Annotated

from fastapi import APIRouter, Header

from app.api.deps import CurrentUser
from app.schemas.site import SiteQrRead
from app.services.core.site_qr import qr_png_data_url, site_origin

router = APIRouter(tags=["site"])


@router.get("/qr", response_model=SiteQrRead)
def read_site_qr(
    user: CurrentUser,
    forwarded_host: Annotated[str | None, Header(alias="X-Forwarded-Host")] = None,
    forwarded_proto: Annotated[str | None, Header(alias="X-Forwarded-Proto")] = None,
    host: Annotated[str | None, Header()] = None,
):
    # Il QR contiene solo l'origine del sito: niente credenziali o token.
    origin = site_origin(
        os.environ.get("HEAT_PUBLIC_URL"),
        host=forwarded_host or host,
        proto=forwarded_proto,
    )
    return SiteQrRead(url=origin, image=qr_png_data_url(origin))
