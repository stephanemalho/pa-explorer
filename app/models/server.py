from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Server(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    host: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    http_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_local: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    accepting_clients: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    href: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    is_v12: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    raw_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cache_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Future: cubes: Mapped[list["Cube"]] = relationship("Cube", back_populates="server")
