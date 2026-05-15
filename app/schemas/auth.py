from typing import Any

from pydantic import BaseModel, EmailStr


class AuthRequest(BaseModel):
    email: EmailStr
    ibm_pa_version: str = "V12"
    credentials_payload: dict[str, Any]


class AuthRequestResponse(BaseModel):
    message: str


class AuthVerifyResponse(BaseModel):
    message: str
