"""
Shared pytest fixtures: a fresh test database per test session, and a
FastAPI TestClient wired to use it instead of your real database.
"""
import os
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

TEST_DATABASE_URL = "postgresql+psycopg://hodgkin_user:changeme@localhost:2006/hodgkin_test_db"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-pytest-only")

from app.database.session import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app import models as _models  # noqa: E402,F401  (registers all models on Base.metadata)
from app.core.limiter import limiter  # noqa: E402

limiter.enabled = False  # disable rate limiting during tests

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Fresh tables for every test function — created before, dropped after."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with the DB dependency overridden to use the test DB."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_payload():
    return {
        "full_name": "Test User",
        "email": "pytestuser@example.com",
        "password": "test1234",
        "date_of_birth": "2000-01-01",
        "gender": "MALE",
    }


@pytest.fixture
def registered_user_token(client, test_user_payload):
    """Registers a user and returns a valid access token for auth'd requests."""
    client.post("/api/auth/register", json=test_user_payload)
    res = client.post(
        "/api/auth/login",
        data={
            "grant_type": "password",
            "username": test_user_payload["email"],
            "password": test_user_payload["password"],
        },
    )
    return res.json()["access_token"]