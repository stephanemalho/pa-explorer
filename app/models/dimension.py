from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Dimension(Base):
    __tablename__ = "dimensions"
    __table_args__ = (UniqueConstraint("server_name", "cube_name", "name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    server_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    cube_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    unique_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    raw_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cache_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
