"""Основной файл приложения FastAPI."""

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, ValidationError, EmailStr, Field, conint, constr
from typing import Optional

from app.database import get_db
from app.models import Product
from app.schemas import ProductCreate, ProductResponse, User, ErrorResponse
from app.exceptions import CustomExceptionA, CustomExceptionB

app = FastAPI(
    title="Контрольная работа №4",
    description="FastAPI приложение с миграциями, обработкой ошибок и тестами",
    version="1.0.0",
)

# ========== Обработчики ошибок (Задание 10.1) ==========


@app.exception_handler(CustomExceptionA)
async def custom_exception_a_handler(request: Request, exc: CustomExceptionA):
    """Обработчик CustomExceptionA."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="CustomExceptionA",
            message=exc.detail.get("message", str(exc.detail))
            if isinstance(exc.detail, dict)
            else exc.detail,
            status_code=exc.status_code,
        ).model_dump(),
    )


@app.exception_handler(CustomExceptionB)
async def custom_exception_b_handler(request: Request, exc: CustomExceptionB):
    """Обработчик CustomExceptionB."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="CustomExceptionB",
            message=exc.detail.get("message", str(exc.detail))
            if isinstance(exc.detail, dict)
            else exc.detail,
            status_code=exc.status_code,
        ).model_dump(),
    )


# ========== Обработчик ошибок валидации (Задание 10.2) ==========


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Пользовательский обработчик ошибок валидации."""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="ValidationError",
            message="; ".join(errors),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        ).model_dump(),
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Обработчик ошибок валидации Pydantic."""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="ValidationError",
            message="; ".join(errors),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        ).model_dump(),
    )


# ========== Эндпоинты для продуктов (Задание 9.1) ==========


@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    """Создание нового продукта."""
    db_product = Product(
        title=product.title,
        price=product.price,
        count=product.count,
        description=product.description,
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Получение продукта по ID."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.get("/products")
async def list_products(db: AsyncSession = Depends(get_db)):
    """Получение списка всех продуктов."""
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return products


# ========== Эндпоинты для демонстрации пользовательских исключений (Задание 10.1) ==========


@app.get("/check-age")
async def check_age(age: int):
    """Эндпоинт, вызывающий CustomExceptionA, если возраст < 18."""
    if age < 18:
        raise CustomExceptionA(f"Age must be at least 18, got {age}")
    return {"message": f"Age {age} is valid", "age": age}


@app.get("/resource/{resource_id}")
async def get_resource(resource_id: int):
    """
    Эндпоинт, вызывающий CustomExceptionB, если resource_id != 1.
    Имитация поиска ресурса.
    """
    if resource_id != 1:
        raise CustomExceptionB(f"Resource with id {resource_id} not found")
    return {"id": resource_id, "name": "Test Resource", "data": "Some data"}


# ========== Эндпоинт для валидации пользователя (Задание 10.2) ==========


@app.post("/users/validate", status_code=status.HTTP_200_OK)
async def validate_user(user: User):
    """Эндпоинт для проверки валидации данных пользователя."""
    return {
        "message": "User data is valid",
        "user": user.model_dump(),
    }


# ========== Эндпоинты для тестирования (Задание 11.1, 11.2) ==========

# In-memory хранилище для пользователей
users_db: dict[int, dict] = {}
_id_counter: int = 1


class UserIn(BaseModel):
    username: str
    age: int = Field(..., gt=18, description="Возраст должен быть больше 18")


class UserOut(BaseModel):
    id: int
    username: str
    age: int


@app.post("/api/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_api_user(user: UserIn):
    """Создание пользователя в in-memory хранилище."""
    global _id_counter
    user_id = _id_counter
    _id_counter += 1
    users_db[user_id] = {"username": user.username, "age": user.age}
    return {"id": user_id, **users_db[user_id]}


@app.get("/api/users/{user_id}", response_model=UserOut)
async def get_api_user(user_id: int):
    """Получение пользователя из in-memory хранилища."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user_id, **users_db[user_id]}


@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_user(user_id: int):
    """Удаление пользователя из in-memory хранилища."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del users_db[user_id]
    return None


@app.get("/health")
async def health_check():
    """Проверка работоспособности приложения."""
    return {"status": "ok"}