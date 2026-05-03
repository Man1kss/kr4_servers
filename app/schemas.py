"""Pydantic схемы для валидации данных."""

from pydantic import BaseModel, EmailStr, Field, conint, constr
from typing import Optional


class ProductBase(BaseModel):
    """Базовая схема продукта."""

    title: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0)
    count: int = Field(..., ge=0)


class ProductCreate(ProductBase):
    """Схема для создания продукта."""

    description: str = Field(..., min_length=1, max_length=1000)


from pydantic import ConfigDict

class ProductResponse(ProductBase):
    """Схема ответа с данными продукта."""

    id: int
    description: str

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    """Схема пользователя для задания 10.2."""

    username: str
    age: conint(gt=18)  # type: ignore
    email: EmailStr
    password: constr(min_length=8, max_length=16)  # type: ignore
    phone: Optional[str] = "Unknown"


class ErrorResponse(BaseModel):
    """Стандартизированный ответ об ошибке."""

    error: str
    message: str
    status_code: int