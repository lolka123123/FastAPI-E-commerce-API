from sqlalchemy.ext.asyncio import AsyncSession

from app.products.schemas import ProductCreate, ProductUpdate
from app.products.models import Product
from app.products.repository import ProductRepository


class ProductService:
    def __init__(self, repository: ProductRepository, session: AsyncSession):
        self.repository = repository
        self.session = session

    async def create_product(self, data: ProductCreate):
        product = Product(**data.model_dump())
        await self.repository.create(product)
        await self.session.commit()
        return product

    async def get_product_by_id(self, product_id: int):
        product = await self.repository.get_by_id(product_id)
        return product

    async def get_all_products(self):
        return await self.repository.get_all()

    async def update_product(self, product_id: int, data: ProductUpdate):
        product = await self.repository.get_by_id(product_id)
        if product is None:
            return None

        update_data = data.model_dump(exclude_unset=True)

        await self.repository.update(product, update_data)
        await self.session.commit()
        return product

    async def delete_product(self, product_id: int):
        product = await self.repository.get_by_id(product_id)
        if product is None:
            return None

        await self.repository.delete(product)
        await self.session.commit()

        return True

