from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class CubeResponse(BaseModel):
    id: int
    name: str
    server_name: str
    last_schema_update: Optional[str] = None
    last_data_update: Optional[str] = None
    last_synced_at: Optional[datetime] = None
    cache_expires_at: Optional[datetime] = None
    created_at: datetime
    raw_data: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)


class CubesListResponse(BaseModel):
    cubes: list[CubeResponse]
    count: int
    from_cache: bool
    cache_expires_at: Optional[datetime] = None
