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


settings = Settings()
