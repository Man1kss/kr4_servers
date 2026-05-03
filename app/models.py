"""Модели SQLAlchemy."""

from sqlalchemy import String, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Product(Base):
    """Модель продукта."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[str] = mapped_column(String(1000), nullable=True, default="")