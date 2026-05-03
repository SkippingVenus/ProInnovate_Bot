"""Configuración de pruebas con base de datos SQLite en memoria."""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set required environment variables before importing app
os.environ.setdefault("SECRET_KEY", "test-secret-key-12345678901234567890")
os.environ.setdefault("ENCRYPTION_KEY", "AHzT1K8FKVn8Qxzq-FvAOSbWk4Yj7_Y5jFpQ-JE72sE=")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("META_WEBHOOK_VERIFY_TOKEN", "test-webhook-token")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")

from app.main import app
from app.core.database import Base, get_db

SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
