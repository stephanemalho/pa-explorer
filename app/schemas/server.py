from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class ServerResponse(BaseModel):
    id: int
    name: str
    display_name: Optional[str] = None
    host: Optional[str] = None
    http_port: Optional[int] = None
    is_local: Optional[bool] = None
    accepting_clients: Optional[bool] = None
    href: Optional[str] = None
    is_v12: Optional[bool] = None
    last_synced_at: Optional[datetime] = None
    cache_expires_at: Optional[datetime] = None
    created_at: datetime
    raw_data: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)


class ServersListResponse(BaseModel):
    servers: list[ServerResponse]
    count: int
    from_cache: bool
    cache_expires_at: Optional[datetime] = None  # design debt: single TTL for all servers
