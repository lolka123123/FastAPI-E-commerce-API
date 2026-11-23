from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
import jwt
from uuid import UUID

from app.db.session import get_session
from app.auth.service import AuthService
from app.auth.repository import RefreshTokenRepository, EmailVerificationRepository, EmailChangeTokenRepository
from app.users.repository import UserRepository
from app.core.security import decode_access_token
from app.users.models import User

async def get_auth_service(session: Annotated[AsyncSession, Depends(get_session)]) -> AuthService:
    users_repository = UserRepository(session)
    refresh_token_repository = RefreshTokenRepository(session)
    email_verification_repository = EmailVerificationRepository(session)
    email_change_repository = EmailChangeTokenRepository(session)

    return AuthService(session=session,
                       repository=users_repository,
                       refresh_token_repository=refresh_token_repository,
                       email_verification_repository=email_verification_repository,
                       email_change_repository=email_change_repository)




oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           session: Annotated[AsyncSession, Depends(get_session)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)

        if not isinstance(payload, dict):
            raise ValueError

        subject = payload.get('sub')

        if not isinstance(subject, str):
            raise ValueError

        user_id = UUID(subject)

    except(jwt.InvalidTokenError, ValueError, TypeError):
        raise credentials_exception

    user = await session.get(User, user_id)

    if user is None or not user.is_active:
        raise credentials_exception

    return user