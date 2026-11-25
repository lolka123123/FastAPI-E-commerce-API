from sqlalchemy import String, Numeric, Boolean, Uuid, DateTime, func, false
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal
import uuid
from datetime import datetime

from app.db.base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.auth.models import RefreshToken

class User(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default='user', nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)

    refresh_tokens: Mapped[list['RefreshToken']] = relationship(
        back_populates='user',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    verification_email_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

