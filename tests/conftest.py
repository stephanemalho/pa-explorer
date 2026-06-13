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

pytest_plugins = [
    "tests.fixtures.database",
    "tests.fixtures.auth",
]
