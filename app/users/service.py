from sqlalchemy import select, func
from sqlalchemy.sql.functions import count
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.repository import UserRepository
from app.users.models import User

class UserService:
    def __init__(
            self,
            session: AsyncSession,
            repository: UserRepository):
        self.session = session
        self.repository = repository

    async def make_admin(self, user: User):
        user.role = 'admin'
        await self.session.commit()


