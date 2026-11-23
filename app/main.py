from fastapi import FastAPI

from app.system.router import router as system_router
from app.products.router import router as products_router
from app.users.router import router as users_router
from app.auth.router import router as auth_router

app = FastAPI(title='Shop')

app.include_router(system_router)
app.include_router(products_router)
app.include_router(users_router)
app.include_router(auth_router)