from fastapi import APIRouter, Depends, HTTPException, status, Response

from app.products.schemas import ProductResponse, ProductCreate, ProductUpdate
from app.products.service import ProductService
from app.products.dependencies import get_product_service

router = APIRouter(prefix="/products", tags=["products"])








@router.get('/', response_model=list[ProductResponse])
async def get_all_products(service: ProductService = Depends(get_product_service)):
    return await service.get_all_products()


@router.get('/{product_id}')
async def get_product_by_id(product_id: int, service: ProductService = Depends(get_product_service)):
    product = await service.get_product_by_id(product_id)

    if product is None:
        raise HTTPException(status_code=404, detail='Product not found')

    return product
@router.post('/', response_model=ProductResponse)
async def create_product(data: ProductCreate, service: ProductService = Depends(get_product_service)):
    return await service.create_product(data)

@router.patch('/{product_id}', response_model=ProductResponse)
async def update_product(product_id: int, data: ProductUpdate, service: ProductService = Depends(get_product_service)):
    product = await service.update_product(product_id, data)
    if product is None:
        raise HTTPException(status_code=404, detail='Product not found')
    return product


@router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, service: ProductService = Depends(get_product_service)):
    deleted = await service.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='Product not found')

    return Response(status_code=status.HTTP_204_NO_CONTENT)


