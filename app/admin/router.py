from fastapi import APIRouter, Depends, Query
from typing import Annotated, Literal

from app.admin.dependencies import get_current_admin, get_admin_service
from app.admin.schemas import AdminUsersResponse
from app.admin.service import AdminService



router = APIRouter(prefix='/admin', tags=['Admin'], dependencies=[Depends(get_current_admin)])



# @router.get('/users', response_model=AdminUsersResponse)
# async def get_users(
#         service: Annotated[AdminService, Depends(get_admin_service)],
#         page: Annotated[int, Query(ge=1)] = 1,
#         page_size: Annotated[int, Query(ge=1, le=100)] = 20,
#         search: Annotated[str | None, Query(min_length=1, max_length=255)] = None,
#         role: Literal['user', 'admin'] | None = None,
#         is_active: bool | None = None,
#         is_verified: bool | None = None,
# ):
#     return await service.get_users(
#         page=page,
#         page_size=page_size,
#         search=search,
#         role=role,
#         is_active=is_active,
#         is_verified=is_verified
#     )