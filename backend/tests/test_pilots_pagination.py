from .test_pilots_api import create_pilot, register


def names(response):
    return [p["name"] for p in response.json()]


def test_list_is_paginated_alphabetically(client):
    register(client)
    for n in (3, 1, 5, 2, 4):
        assert create_pilot(client, f"Pilota {n}").status_code == 201
    r = client.get("/api/pilots?limit=2&offset=0")
    assert r.status_code == 200
    assert names(r) == ["Pilota 1", "Pilota 2"]
    assert names(client.get("/api/pilots?limit=2&offset=2")) == ["Pilota 3", "Pilota 4"]
    assert names(client.get("/api/pilots?limit=2&offset=4")) == ["Pilota 5"]
    assert client.get("/api/pilots?limit=2&offset=10").json() == []


def test_list_without_params_returns_the_first_page(client):
    register(client)
    for n in range(1, 4):
        create_pilot(client, f"Pilota {n}")
    assert len(client.get("/api/pilots").json()) == 3


def test_list_rejects_invalid_pagination(client):
    register(client)
    assert client.get("/api/pilots?limit=0").status_code == 422
    assert client.get("/api/pilots?limit=101").status_code == 422
    assert client.get("/api/pilots?offset=-1").status_code == 422


def test_pages_only_contain_own_pilots(make_client):
    first, second = make_client(), make_client()
    register(first, "mario")
    register(second, "luigi")
    create_pilot(first, "Pilota A")
    create_pilot(second, "Pilota B")
    assert names(first.get("/api/pilots?limit=10")) == ["Pilota A"]
    assert names(second.get("/api/pilots?limit=10&offset=1")) == []
