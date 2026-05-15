from typing import Any

from pydantic import BaseModel


# TODO Phase 2 : remplacer str par EmailStr (ajouter email-validator aux dépendances)
class AuthRequest(BaseModel):
    email: str
    ibm_pa_version: str = "V12"
    credentials_payload: dict[str, Any]
