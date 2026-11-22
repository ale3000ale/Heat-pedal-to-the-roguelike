import base64

import pytest

from app.db.models import User
from app.security import hash_password
from app.services.core.site_qr import (
    DEFAULT_ORIGIN,
    normalize_origin,
    qr_png_data_url,
    site_origin,
)

PASSWORD = "password123"
PNG_PREFIX = "data:image/png;base64,"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def make_user(make_client, session_factory, username="mario", role="player"):
    client = make_client()
    with session_factory() as db:
        db.add(User(username=username, password=hash_password(PASSWORD), role=role))
        db.commit()
    r = client.post("/api/auth/login", json={"username": username, "password": PASSWORD})
    assert r.status_code == 200
    return client


def test_qr_requires_login(client):
    assert client.get("/api/site/qr").status_code == 401


def test_qr_uses_public_url_before_request(make_client, session_factory, monkeypatch):
    monkeypatch.setenv("HEAT_PUBLIC_URL", "http://192.168.1.50:5173")
    client = make_user(make_client, session_factory)
    r = client.get(
        "/api/site/qr",
        headers={"Host": "localhost:5173", "X-Forwarded-Host": "localhost:5173"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["url"] == "http://192.168.1.50:5173"
    assert data["image"].startswith(PNG_PREFIX)


def test_qr_falls_back_to_request_host(make_client, session_factory, monkeypatch):
    monkeypatch.delenv("HEAT_PUBLIC_URL", raising=False)
    client = make_user(make_client, session_factory)
    r = client.get(
        "/api/site/qr",
        headers={"Host": "127.0.0.1:5173", "X-Forwarded-Host": "192.168.1.50:5173"},
    )
    assert r.status_code == 200
    assert r.json()["url"] == "http://192.168.1.50:5173"


def test_qr_uses_forwarded_proto(make_client, session_factory, monkeypatch):
    monkeypatch.delenv("HEAT_PUBLIC_URL", raising=False)
    client = make_user(make_client, session_factory)
    r = client.get(
        "/api/site/qr",
        headers={"Host": "192.168.1.50:5173", "X-Forwarded-Proto": "https"},
    )
    assert r.json()["url"] == "https://192.168.1.50:5173"


def test_qr_is_png(make_client, session_factory, monkeypatch):
    monkeypatch.setenv("HEAT_PUBLIC_URL", "http://192.168.1.50:5173")
    client = make_user(make_client, session_factory)
    image = client.get("/api/site/qr").json()["image"]
    raw = base64.b64decode(image[len(PNG_PREFIX) :])
    assert raw.startswith(PNG_SIGNATURE)


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "   ",
        "ftp://192.168.1.50:5173",
        "http://user:secret@192.168.1.50:5173",
        "http://192.168.1.50:5173/path",
        "http://192.168.1.50:5173?q=1",
        "http://192.168.1.50:5173#fragment",
        "http://192.168.1.50:not-a-port",
        "http://192.168.1.50:5173 due",
    ],
)
def test_normalize_origin_rejects_invalid_values(value):
    assert normalize_origin(value) is None


def test_normalize_origin_accepts_host_and_origin():
    assert normalize_origin("http://192.168.1.50:5173") == "http://192.168.1.50:5173"
    assert normalize_origin("192.168.1.50:5173") == "http://192.168.1.50:5173"
    assert normalize_origin("https://heat.local:5173/") == "https://heat.local:5173"


def test_site_origin_precedence():
    assert site_origin("http://10.0.0.5:5173", host="192.168.1.9:5173") == "http://10.0.0.5:5173"
    assert site_origin(None, host="192.168.1.9:5173") == "http://192.168.1.9:5173"
    assert (
        site_origin("non valido", host="192.168.1.9:5173", proto="https")
        == "https://192.168.1.9:5173"
    )
    assert site_origin(None) == DEFAULT_ORIGIN


def test_site_origin_takes_first_forwarded_value():
    assert (
        site_origin(None, host="192.168.1.9:5173, proxy", proto="http, https")
        == "http://192.168.1.9:5173"
    )


def test_qr_png_data_url():
    data = qr_png_data_url("http://192.168.1.50:5173")
    assert data.startswith(PNG_PREFIX)
    assert base64.b64decode(data[len(PNG_PREFIX) :]).startswith(PNG_SIGNATURE)
