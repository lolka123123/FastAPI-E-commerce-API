from fastapi import FastAPI
from sqladmin import Admin

from app.core.config import settings

from app.db.session import engine, async_session_maker
from app.admin_panel.views import UserAdmin
from app.admin_panel.authentication import AdminAuth, RoleAuthorization

from app.system.router import router as system_router
from app.products.router import router as products_router
from app.users.router import router as users_router
from app.auth.router import router as auth_router
from app.admin.router import router as admin_router

app = FastAPI(title='Shop')

admin = Admin(
    app=app,
    engine=engine,
    session_maker=async_session_maker,
    title='Administration',
    authentication_backend=AdminAuth(
        secret_key=settings.secret_key
    ),
    authorization_backend=RoleAuthorization()
)
admin.add_view(UserAdmin)



app.include_router(system_router)
app.include_router(products_router)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(admin_router)
