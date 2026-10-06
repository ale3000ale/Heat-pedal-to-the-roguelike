from .test_pilots_api import create_pilot, create_team, register


def names(response):
    return [p["name"] for p in response.json()]


def make_pilots(client):
    for name in ("Ayrton Senna", "Niki Lauda", "Senna Junior"):
        assert create_pilot(client, name).status_code == 201


def test_search_matches_part_of_the_name_ignoring_case(client):
    register(client)
    make_pilots(client)
    assert names(client.get("/api/pilots?q=senna")) == ["Ayrton Senna", "Senna Junior"]
    assert names(client.get("/api/pilots?q=SENNA")) == ["Ayrton Senna", "Senna Junior"]
    assert names(client.get("/api/pilots?q=%20lauda%20")) == ["Niki Lauda"]
    assert client.get("/api/pilots?q=zzz").json() == []


def test_blank_search_returns_everything(client):
    register(client)
    make_pilots(client)
    assert len(client.get("/api/pilots?q=").json()) == 3
    assert len(client.get("/api/pilots?q=%20%20").json()) == 3


def test_wildcards_are_taken_literally(client):
    register(client)
    make_pilots(client)
    assert client.get("/api/pilots?q=%25").json() == []
    assert client.get("/api/pilots?q=_").json() == []


def test_search_is_limited_to_own_pilots(make_client):
    first, second = make_client(), make_client()
    register(first, "mario")
    register(second, "luigi")
    create_pilot(first, "Ayrton Senna")
    assert names(first.get("/api/pilots?q=senna")) == ["Ayrton Senna"]
    assert second.get("/api/pilots?q=senna").json() == []


def test_search_text_has_a_maximum_length(client):
    register(client)
    assert client.get(f"/api/pilots?q={'a' * 41}").status_code == 422
    assert client.get(f"/api/pilots?q={'a' * 40}").status_code == 200


def test_filter_by_team(client):
    register(client)
    red = create_team(client, "Rossa")
    blue = create_team(client, "Blu")
    create_pilot(client, "Pilota Uno", red)
    create_pilot(client, "Pilota Due", blue)
    create_pilot(client, "Pilota Tre", red)
    create_pilot(client, "Senza Team")
    assert names(client.get(f"/api/pilots?team_id={red}")) == ["Pilota Tre", "Pilota Uno"]
    assert names(client.get(f"/api/pilots?team_id={blue}")) == ["Pilota Due"]
    assert client.get("/api/pilots?team_id=999").json() == []


def test_foreign_team_filter_gives_no_results(make_client):
    first, second = make_client(), make_client()
    register(first, "mario")
    register(second, "luigi")
    foreign = create_team(second, "Altrui")
    create_pilot(second, "Pilota Altrui", foreign)
    create_pilot(first, "Pilota Mio")
    assert first.get(f"/api/pilots?team_id={foreign}").json() == []


def test_search_team_filter_and_pagination_combine(client):
    register(client)
    team = create_team(client, "Rossa")
    for n in range(1, 5):
        create_pilot(client, f"Pilota {n}", team)
    create_pilot(client, "Altro 1", team)
    url = f"/api/pilots?q=pilota&team_id={team}"
    assert names(client.get(f"{url}&limit=2&offset=0")) == ["Pilota 1", "Pilota 2"]
    assert names(client.get(f"{url}&limit=2&offset=2")) == ["Pilota 3", "Pilota 4"]
    assert client.get(f"{url}&limit=2&offset=4").json() == []
