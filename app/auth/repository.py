from unittest import result

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timezone
import uuid

from app.auth.models import RefreshToken, EmailVerificationToken, EmailChangeToken

class RefreshTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        self.session.add(refresh_token)
        await self.session.flush()
        return refresh_token

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def revoke(self, refresh_token: RefreshToken) -> None:
        refresh_token.revoked_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def revoke_all(self, user_id: uuid.UUID) -> None:
        stmp = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None)
            )
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await self.session.execute(stmp)


class EmailVerificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, verification_token: EmailVerificationToken) -> EmailVerificationToken:
        self.session.add(verification_token)
        await self.session.flush()
        return verification_token

    async def get_by_hush(self, token_hash: str) -> EmailVerificationToken | None:
        result = await self.session.execute(
            select(EmailVerificationToken)
            .where(EmailVerificationToken.token_hash == token_hash)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def mark_as_used(self, verification_token: EmailVerificationToken) -> None:
        verification_token.used_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def invalidate_pending_for_user(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(EmailVerificationToken)
            .where(
                EmailVerificationToken.user_id == user_id,
                EmailVerificationToken.used_at.is_(None)
            )
            .values(used_at=datetime.now(timezone.utc))
        )
        await self.session.execute(stmt)


class EmailChangeTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, token: EmailChangeToken) -> EmailChangeToken:
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_by_hash(self,token_hash: str) -> EmailChangeToken | None:
        result = await self.session.execute(
            select(EmailChangeToken)
            .where(EmailChangeToken.token_hash == token_hash)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def invalidate_pending(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(EmailChangeToken)
            .where(EmailChangeToken.user_id == user_id,
                   EmailChangeToken.used_at.is_(None))
            .values(used_at=datetime.now(timezone.utc))
        )
        await self.session.execute(stmt)

    async def mark_as_used(self, token: EmailChangeToken) -> None:
        token.used_at = datetime.now(timezone.utc)
        await self.session.flush()
