import pytest

from app.schemas.auth import UserRead


@pytest.mark.parametrize("role", ["admin", "judge", "player"])
def test_user_read_accepts_every_role(role):
    # Il login restituisce UserRead: un ruolo non ammesso qui dà errore 500.
    user = UserRead(id=1, username="x", role=role)
    assert user.role == role


def test_user_read_rejects_unknown_role():
    with pytest.raises(ValueError):
        UserRead(id=1, username="x", role="boss")
