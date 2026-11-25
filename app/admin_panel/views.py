import uuid

from sqladmin import ModelView, action, Flash
from sqladmin.filters import BooleanFilter, StaticValuesFilter
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.db.session import async_session_maker
from app.users.models import User
from app.users.repository import UserRepository
from app.admin.service import AdminService

from app.auth.repository import RefreshTokenRepository

from app.admin.exceptions import InsufficientPermissionsError, UserNotFoundError

class UserAdmin(ModelView, model=User):
    name = 'Пользователь'
    name_plural = 'Пользователи'
    icon = 'fa-solid fa-users'


    column_list = [
        User.id,
        User.email,
        User.role,
        User.is_active,
        User.is_verified,
        User.created_at,
    ]

    column_labels = {
        User.id: 'ID',
        User.email: 'Email',
        User.role: 'Роль',
        User.is_active: 'Активен',
        User.is_verified: 'Email подтвержден',
        User.created_at: 'Дата регистрации',
    }

    column_searchable_list = [User.email]
    column_sortable_list = [
        User.email,
        User.created_at
    ]
    column_default_sort = [(User.created_at, True)]

    column_filters = [
        BooleanFilter(User.is_active),
        BooleanFilter(User.is_verified),
        StaticValuesFilter(
            User.role,
            [
                ('user', 'Пользователь'),
                ('admin', 'Администратор'),
                # ('superadmin', 'СуперАдминистратор'),
            ],
            title='Роль'
        )
    ]

    column_details_exclude_list = [
        'refresh_tokens',
        'hashed_password',
        'verification_email_sent_at',
    ]



    form_excluded_columns = [
        User.id,
        User.hashed_password,
        User.created_at,
        User.verification_email_sent_at,
        User.refresh_tokens
    ]



    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    page_size = 20
    page_size_options = [20, 50, 100]


    @action(
        name='block-users',
        label='Заблокировать',
        confirmation_message='Заблокировать выбранных пользователей?'
    )
    async def block_users(self, request: Request):
        users_ids = request.query_params.get("pks", "").split(",")
        users_ids = [uuid.UUID(user_id) for user_id in users_ids if user_id]

        admin_id = request.session.get('admin_user_id')

        if not admin_id:
            return False

        async with async_session_maker() as session:
            admin_service = AdminService(
                session=session,
            )
            current_admin = await admin_service.get_user_by_id(uuid.UUID(admin_id))

            if current_admin is None:
                return False

            # print(f'{current_admin.}')

            try:
                await admin_service.block_users(
                    users_ids=users_ids,
                    current_admin=current_admin
                )
            except UserNotFoundError:
                Flash.error(request, 'Пользователь не найден')

            except InsufficientPermissionsError as e:
                Flash.error(request, str(e))

            else:
                Flash.success(request, 'Операция выполнена')
            return RedirectResponse(
                request.headers.get('Referer', '/admin'),
                status_code=303,
            )


    @action(
        name='unblock-users',
        label='Разблокировать',
        confirmation_message='Разблокировать выбранных пользователей?'
    )
    async def unblock_users(self, request: Request):
        users_ids = request.query_params.get("pks", "").split(",")
        users_ids = [uuid.UUID(user_id) for user_id in users_ids if user_id]

        admin_id = request.session.get('admin_user_id')

        if not admin_id:
            return False

        async with async_session_maker() as session:
            admin_service = AdminService(
                session=session,
            )
            current_admin = await admin_service.get_user_by_id(uuid.UUID(admin_id))

            if current_admin is None:
                return False

            try:
                await admin_service.unblock_user(
                    users_ids=users_ids,
                    current_admin=current_admin
                )
            except UserNotFoundError:
                Flash.error(request, 'Пользователь не найден')

            except InsufficientPermissionsError as e:
                Flash.error(request, str(e))

            else:
                Flash.success(request, 'Операция выполнена')
            return RedirectResponse(
                request.headers.get('Referer', '/admin'),
                status_code=303,
            )


