from typing import Annotated
from fastapi import APIRouter, Depends

from app.users.models import User
from app.auth.dependencies import get_current_user
from app.users.dependencies import get_user_service
from app.users.service import UserService
from app.users.schemas import UserResponse


router = APIRouter(prefix="/users", tags=["users"])



# @router.get("/me", response_model=UserResponse)
@router.get("/me", response_model=UserResponse)
async def get_me(
    user: Annotated[User, Depends(get_current_user)]
):
    return user


# @router.post('/make-admin')
# async def make_admin(
#         current_user: Annotated[User, Depends(get_current_user)],
#         service: Annotated[UserService, Depends(get_user_service)]
# ):
#     await service.make_admin(current_user)
#     return {'message': 'zaebis'}



# @router.get("/", response_model=list[UserResponse])
# async def get_all_users(service: Annotated[UserService, Depends(get_user_service)]):
#     return await service.get_all()