import uuid
from datetime import datetime, timezone, timedelta

from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from app.users.repository import UserRepository
from app.users.models import User
from app.auth.schemas import RegisterRequest, TokenPair
from app.auth.repository import RefreshTokenRepository, EmailVerificationRepository, EmailChangeTokenRepository
from app.auth.models import RefreshToken, EmailVerificationToken, EmailChangeToken

from app.core.security import hash_password, verify_password, create_access_token, generate_secure_token, hash_secure_token
from app.core.config import settings
from app.core.email import send_verification_email, send_email_change_email


class RegisterStatus(str, Enum):
    CREATED = 'created'
    ALREADY_REGISTERED = 'already_registered'
    RATE_LIMIT = 'rate_limit'



class AuthService:
    def __init__(self, session: AsyncSession,
                 repository: UserRepository,
                 refresh_token_repository: RefreshTokenRepository,
                 email_verification_repository: EmailVerificationRepository,
                 email_change_repository: EmailChangeTokenRepository):
        self.session = session
        self.repository = repository
        self.refresh_token_repository = refresh_token_repository
        self.email_verification_repository = email_verification_repository
        self.email_change_repository = email_change_repository


    async def register(self, data: RegisterRequest) -> RegisterStatus:
        existing_user = await self.repository.get_by_email(str(data.email))
        if existing_user:
            if existing_user.is_verified:
                return RegisterStatus.ALREADY_REGISTERED

            if not self.can_send_verification_email(existing_user):
                return RegisterStatus.RATE_LIMIT

            user = existing_user
            user.hashed_password = hash_password(data.password)

            await self.email_verification_repository.invalidate_pending_for_user(user_id=user.id)
        else:
            user = User(email=str(data.email),
                        hashed_password=hash_password(data.password),
                        is_verified=False)

            await self.repository.create(user)

        verification_token = generate_secure_token()
        verification_token_hash = hash_secure_token(verification_token)

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.email_verification_expire_minutes)

        db_token = EmailVerificationToken(
            user_id=user.id,
            token_hash=verification_token_hash,
            expires_at=expires_at
        )
        await self.email_verification_repository.create(db_token)

        user.verification_email_sent_at = datetime.now(timezone.utc)

        await self.session.commit()
        await self.session.refresh(user)

        await send_verification_email(
            recipient=user.email,
            token=verification_token
        )

        return RegisterStatus.CREATED

    async def login(self, email: str, password: str) -> TokenPair | None:
        user = await self.repository.get_by_email(email)
        if user is None:
            return None

        if not user.is_verified:
            return None

        if not user.is_active:
            return None

        if not verify_password(password, user.hashed_password):
            return None


        access_token = create_access_token(str(user.id))

        refresh_token = generate_secure_token()
        refresh_token_hash = hash_secure_token(refresh_token)

        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)


        db_token = RefreshToken(user_id=user.id,
                                token_hash=refresh_token_hash,
                                expires_at=expires_at)

        await self.refresh_token_repository.create(db_token)
        await self.session.commit()

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def refresh(self, token: str) -> TokenPair | None:
        token_hash = hash_secure_token(token)

        db_token = await self.refresh_token_repository.get_by_hash(token_hash)
        if db_token is None:
            return None

        now = datetime.now(timezone.utc)

        if db_token.revoked_at is not None:
            return None

        if db_token.expires_at <= now:
            return None

        user = await self.session.get(User, db_token.user_id)

        if user is None or not user.is_active:
            return None

        await self.refresh_token_repository.revoke(db_token)

        access_token = create_access_token(str(user.id))

        refresh_token = generate_secure_token()
        refresh_token_hash = hash_secure_token(refresh_token)

        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)

        new_db_token = RefreshToken(
            user_id=user.id,
            token_hash=refresh_token_hash,
            expires_at=expires_at
        )

        await self.refresh_token_repository.create(new_db_token)

        await self.session.commit()

        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def verify_email(self, token: str) -> bool:
        token_hash = hash_secure_token(token)

        verification_token = await self.email_verification_repository.get_by_hush(token_hash)

        if verification_token is None:
            return False

        now = datetime.now(timezone.utc)

        if (
            verification_token.used_at is not None
            or verification_token.expires_at <= now
        ):
            return False

        user = await self.session.get(User, verification_token.user_id)

        if user is None:
            return False

        user.is_verified = True

        await self.email_verification_repository.mark_as_used(verification_token=verification_token)

        await self.session.commit()

        return True

    async def resend_verification(self, email: str) -> RegisterStatus | None:
        user = await self.repository.get_by_email(email)
        if user is None or user.is_verified:
            return

        if not self.can_send_verification_email(user):
            return RegisterStatus.RATE_LIMIT

        await self.email_verification_repository.invalidate_pending_for_user(user_id=user.id)

        verification_token = generate_secure_token()
        verification_token_hash = hash_secure_token(verification_token)

        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.email_verification_expire_minutes
        )

        db_token = EmailVerificationToken(
            user_id=user.id,
            token_hash=verification_token_hash,
            expires_at=expires_at
        )

        await self.email_verification_repository.create(db_token)

        user.verification_email_sent_at = datetime.now(timezone.utc)

        await self.session.commit()

        await send_verification_email(
            recipient=user.email,
            token=verification_token
        )

    def can_send_verification_email(self, user: User) -> bool:
        if user.verification_email_sent_at is None:
            return True

        now = datetime.now(timezone.utc)
        return now - user.verification_email_sent_at >= timedelta(seconds=60)

    async def logout(self, refresh_token: str) -> None:
        token_hash = hash_secure_token(refresh_token)

        db_token = await self.refresh_token_repository.get_by_hash(token_hash)

        if db_token is None:
            return

        if db_token.revoked_at is not None:
            return

        await self.refresh_token_repository.revoke(db_token)

        await self.session.commit()

    async def logout_all(self, used_id: uuid.UUID) -> None:
        await self.refresh_token_repository.revoke_all(used_id)
        await self.session.commit()


    async def change_password(self, user: User,
                              current_password: str,
                              new_password: str) -> bool:
        if not verify_password(password=current_password,
                               hashed_password=user.hashed_password):
            return False

        if current_password == new_password:
            return False

        user.hashed_password = hash_password(new_password)

        await self.refresh_token_repository.revoke_all(user_id=user.id)

        await self.session.commit()

        return True

    async def request_email_change(self, user: User,
                                   new_email: str,
                                   current_password: str) -> bool:
        if not self.can_send_verification_email(user):
            return False

        if not verify_password(current_password, user.hashed_password):
            return False

        new_email = new_email.lower().strip()

        if new_email == user.email.lower():
            return False

        existing_user = await self.repository.get_by_email(new_email)

        if existing_user is not None:
            if existing_user.is_verified:
                return False



        await self.email_change_repository.invalidate_pending(user.id)

        token = generate_secure_token()
        token_hash = hash_secure_token(token)

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.email_verification_expire_minutes)

        db_token = EmailChangeToken(
            user_id=user.id,
            new_email=new_email,
            token_hash=token_hash,
            expires_at=expires_at
        )

        await self.email_change_repository.create(db_token)

        user.verification_email_sent_at = datetime.now(timezone.utc)

        await self.session.commit()

        await send_email_change_email(
            recipient=new_email,
            token=token
        )

        return True

    async def confirm_email_change(self, token: str) -> bool:
        token_hash = hash_secure_token(token)

        db_token = await self.email_change_repository.get_by_hash(token_hash)

        if db_token is None:
            return False

        now = datetime.now(timezone.utc)

        if db_token.used_at is not None or db_token.expires_at <= now:
            return False

        user = await self.session.get(User, db_token.user_id)

        if user is None:
            return False

        existing_user = await self.repository.get_by_email(db_token.new_email)

        if existing_user is not None and existing_user.id != user.id:
            if existing_user.is_verified:
                return False
            await self.repository.delete(existing_user)

        user.email = db_token.new_email
        user.is_verified = True

        await self.email_change_repository.mark_as_used(db_token)

        await self.session.commit()

        return True

    async def delete_user(self, email: str):
        user = await self.repository.get_by_email(email)

        if user is None:
            return False

        await self.repository.delete(user)
        await self.session.commit()

        return True




