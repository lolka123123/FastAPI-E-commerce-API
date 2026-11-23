from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal

from app.db.base import Base

class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10,2), nullable=False)