
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.products.models import Product

class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, product: Product):
        self.session.add(product)
        await self.session.flush()

        return product

    async def get_by_id(self, product_id: int):
        stmt = select(Product).where(Product.id == product_id)
        return await self.session.scalar(stmt)


    async def get_all(self):
        stmt = select(Product)
        result = await self.session.scalars(stmt)
        return result.all()

    async def update(self, product: Product, data: dict):
        for field, value in data.items():
            setattr(product, field, value)
        await self.session.flush()
        return product

    async def delete(self, product: Product):
        await self.session.delete(product)