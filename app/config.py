from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "pa-explorer"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./pa_explorer.db"

    # IBM Planning Analytics
    ibm_pa_base_url: str
    ibm_pa_tenant_id: str
    ibm_pa_api_key: str
    ibm_pa_servers_ttl_seconds: int = 300
    ibm_pa_cubes_ttl_seconds: int = 300
    ibm_pa_dimensions_ttl_seconds: int = 300

    # Auth
    pa_explorer_encryption_key: str
    pa_explorer_initial_admin_email: str
    auth_session_ttl_hours: int = 24
    auth_magic_link_ttl_minutes: int = 15

    @field_validator("debug", mode="before")
    @classmethod
    def _parse_debug(cls, value):
        if isinstance(value, str) and value.strip().lower() == "release":
            return False
        return value


settings = Settings()
