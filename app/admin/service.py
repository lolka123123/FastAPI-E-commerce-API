import uuid
from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from math import ceil

from sqlalchemy.sql.functions import user

from app.users.repository import UserRepository
from app.users.models import User

from app.auth.repository import RefreshTokenRepository

from app.admin.exceptions import InsufficientPermissionsError, UserNotFoundError

class AdminService:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.user_repository = UserRepository(session)
        self.refresh_token_repository = RefreshTokenRepository(session)

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        user = await self.user_repository.get_by_id(user_id)
        return user

    async def block_users(self, users_ids: list[uuid.UUID], current_admin: User) -> None:
        users = []
        for user_id in users_ids:
            user = await self.user_repository.get_by_id(user_id)
            if user is None:
                raise UserNotFoundError('User not found')

            if current_admin.role == 'admin' and user.role != 'user':
                raise InsufficientPermissionsError('Admin can only block regular users')

            if current_admin.role == 'superadmin' and user.role == 'superadmin':
                raise InsufficientPermissionsError('Cannot block another superadmin')

            users.append(user)

        for user in users:
            user.is_active = False
            await self.refresh_token_repository.revoke_all(user.id)

        await self.session.commit()


    async def unblock_user(self, users_ids: list[uuid.UUID], current_admin: User) -> None:
        users = []
        for user_id in users_ids:
            user = await self.user_repository.get_by_id(user_id)

            if user is None:
                raise UserNotFoundError('User not found')

            if current_admin.role == 'admin' and user.role != 'user':
                raise InsufficientPermissionsError('Admin can only unblock regular users')

            if current_admin.role == 'superadmin' and user.role == 'superadmin':
                raise InsufficientPermissionsError('Cannot unblock another superadmin')


            users.append(user)

        for user in users:
            user.is_active = True

        await self.session.commit()




    async def get_users(
            self,
            page: int = 1,
            page_size: int = 20,
            search: str | None = None,
            role: str | None = None,
            is_active: bool | None = None,
            is_verified: bool | None = None
    ) -> dict:

        users, total = await self.user_repository.get_all(
            page=page,
            page_size=page_size,
            search=search,
            role=role,
            is_active=is_active,
            is_verified=is_verified
        )

        return {
            'items': users,
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': ceil(total / page_size) if total else 0
        }
