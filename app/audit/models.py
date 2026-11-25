import uuid
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, ForeignKey, Uuid, func, JSON
from app.db.base import Base
from app.users.models import User

class AdminLog(Base):
    __tablename__ = 'admin_logs'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    admin_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    target_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    derails: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
