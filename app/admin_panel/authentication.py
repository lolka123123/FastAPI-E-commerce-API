from typing import Any

from sqladmin.authentication import AuthenticationBackend
from sqladmin.authorization import AuthorizationBackend, Action
from starlette.requests import Request
from starlette.responses import Response

from sqlalchemy import select

import uuid

from app.db.session import async_session_maker
from app.users.models import User
from app.core.security import verify_password

from app.admin_panel.views import UserAdmin


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> Response | bool:
        form = await request.form()

        email = form.get('username')
        password = form.get('password')

        if not email or not  password:
            return False

        async with async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()

            if user is None:
                return False

            if not verify_password(
                    password=str(password),
                    hashed_password=user.hashed_password):
                return False

            if user.role not in ('admin', 'superadmin') or not user.is_active:
                return False

            request.session.update(
                {'admin_user_id': str(user.id)}
            )

            return True

    async def authenticate(self, request: Request) -> Response | bool:
        user_id = request.session.get('admin_user_id')

        if not user_id:
            return False

        try:
            user_uuid = uuid.UUID(user_id)
        except (ValueError, TypeError):
            return False

        async with async_session_maker() as session:
            user = await session.get(User, user_uuid)

            if user is None:
                return False

            if user.role not in ('admin', 'superadmin') or not user.is_active:
                return False

            request.session['admin_role'] = user.role

            return True


    async def logout(self, request: Request) -> Response | bool:
        request.session.clear()
        return True


class RoleAuthorization(AuthorizationBackend):
    def has_permission(
        self,
        request: Request,
        identity: str,
        action: str,
        obj: Any | None = None,
    ) -> bool:
        role = request.session.get('admin_role')

        if role == 'superadmin':
            return True

        if role == 'admin':
            return (identity == 'user'
                    and action in (
                        Action.LIST,
                        Action.DETAILS,
                        'action:block-users',
                        'action:unblock-users',
                    ))

        return False