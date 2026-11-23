from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.users.models import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )

        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_all(self) -> list[User]:
        result = await self.session.scalars(
            select(User)
        )

        return list(result.all())

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.flush()


