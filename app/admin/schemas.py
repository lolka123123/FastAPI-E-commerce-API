from pydantic import BaseModel

from app.users.schemas import UserResponse

class AdminUsersResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    pages: int

