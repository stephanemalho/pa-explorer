import os

from cryptography.fernet import Fernet

# Positionner les variables d'environnement AVANT tout import applicatif.
# setdefault ne surcharge pas les valeurs présentes dans .env.local.
os.environ.setdefault("PA_EXPLORER_ENCRYPTION_KEY", Fernet.generate_key().decode())
os.environ.setdefault("IBM_PA_BASE_URL", "https://test.example.com")
os.environ.setdefault("IBM_PA_TENANT_ID", "test-tenant")
os.environ.setdefault("IBM_PA_API_KEY", "test-api-key")
os.environ.setdefault("PA_EXPLORER_INITIAL_ADMIN_EMAIL", "test@example.com")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
