import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.db.models  # noqa: F401
from app.db.base import Base
from app.db.session import get_db
from app.main import app as main_app


@pytest.fixture()
def session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _enable_fk(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    yield sessionmaker(autocommit=False, autoflush=False, bind=engine)
    engine.dispose()


@pytest.fixture()
def make_client(session_factory):
    created = []

    def _make(app_obj=main_app):
        def _get_test_db():
            db = session_factory()
            try:
                yield db
            finally:
                db.close()

        app_obj.dependency_overrides[get_db] = _get_test_db
        created.append(app_obj)
        return TestClient(app_obj)

    yield _make
    for app_obj in created:
        app_obj.dependency_overrides.clear()


@pytest.fixture()
def client(make_client):
    return make_client()