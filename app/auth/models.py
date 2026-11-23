from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid, ForeignKey, String, DateTime, func

import uuid
from datetime import datetime

from  app.db.base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.users.models import User

class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid,
                                               ForeignKey('users.id', ondelete='CASCADE'),
                                               nullable=False,
                                               index=True
                                               )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped['User'] = relationship(back_populates='refresh_tokens')


class EmailVerificationToken(Base):
    __tablename__ = 'email_verification_tokens'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid,
                                               ForeignKey('users.id', ondelete='CASCADE'),
                                               nullable=False,
                                               index=True
                                               )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped['User'] = relationship()


class EmailChangeToken(Base):
    __tablename__ = 'email_change_tokens'

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid,
                                               ForeignKey('users.id', ondelete='CASCADE'),
                                               nullable=False,
                                               index=True
                                               )
    new_email: Mapped[str] = mapped_column(String(255), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped['User'] = relationship()