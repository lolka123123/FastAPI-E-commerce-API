from fastapi import Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.users.models import User
from app.auth.dependencies import get_current_user
from app.admin.service import AdminService
from app.users.repository import UserRepository

from app.auth.repository import RefreshTokenRepository

async def get_current_admin(
        current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role not in ('admin', 'superadmin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Admin success required'
        )
    return current_user

async def get_admin_service(session: Annotated[AsyncSession, Depends(get_session)]) -> AdminService:

    return AdminService(
        session=session
    )
