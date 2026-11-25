import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.users.models import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )

        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        user = await self.session.get(User, user_id)
        return user

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user


    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.flush()

    async def get_all(
            self,
            page: int = 1,
            page_size: int = 20,
            search: str | None = None,
            role: str | None = None,
            is_active: bool | None = None,
            is_verified: bool | None = None
    ) -> tuple[list[User], int]:
        stmt = select(User)
        count_stmt = select(func.count(User.id))

        if search:
            filter_condition = User.email.ilike(f'%{search}%')
            stmt = stmt.where(filter_condition)
            count_stmt = count_stmt.where(filter_condition)

        if role is not None:
            stmt = stmt.where(User.role == role)
            count_stmt = count_stmt.where(User.role == role)

        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)
            count_stmt = count_stmt.where(User.is_active == is_active)

        if is_verified is not None:
            stmt = stmt.where(User.is_verified == is_verified)
            count_stmt = count_stmt.where(User.is_verified == is_verified)


        total = await self.session.scalar(count_stmt)

        stmt = (
            stmt
            .order_by(User.created_at.desc())
            .offset((page-1)*page_size)
            .limit(page_size)
        )

        result = await self.session.scalars(stmt)

        return list(result.all()), total or 0



