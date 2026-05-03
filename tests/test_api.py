"""Модульные тесты для API (Задание 11.1)."""

import pytest
from fastapi.testclient import TestClient


class TestUserEndpoints:
    """Тесты для эндпоинтов работы с пользователями."""

    def test_create_user_success(self, client: TestClient):
        """Тест успешного создания пользователя."""
        response = client.post(
            "/api/users",
            json={"username": "testuser", "age": 25},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["username"] == "testuser"
        assert data["age"] == 25

    def test_create_user_invalid_data(self, client: TestClient):
        """Тест создания пользователя с невалидными данными."""
        response = client.post(
            "/api/users",
            json={"username": "testuser", "age": 16},
        )
        assert response.status_code == 422

    def test_get_user_success(self, client: TestClient):
        """Тест успешного получения пользователя."""
        create_response = client.post(
            "/api/users",
            json={"username": "testuser", "age": 25},
        )
        user_id = create_response.json()["id"]

        response = client.get(f"/api/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == "testuser"
        assert data["age"] == 25

    def test_get_user_not_found(self, client: TestClient):
        """Тест получения несуществующего пользователя."""
        response = client.get("/api/users/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_delete_user_success(self, client: TestClient):
        """Тест успешного удаления пользователя."""
        create_response = client.post(
            "/api/users",
            json={"username": "testuser", "age": 25},
        )
        user_id = create_response.json()["id"]

        response = client.delete(f"/api/users/{user_id}")
        assert response.status_code == 204

        get_response = client.get(f"/api/users/{user_id}")
        assert get_response.status_code == 404

    def test_delete_user_not_found(self, client: TestClient):
        """Тест удаления несуществующего пользователя."""
        response = client.delete("/api/users/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_create_multiple_users(self, client: TestClient):
        """Тест создания нескольких пользователей."""
        response1 = client.post(
            "/api/users",
            json={"username": "user1", "age": 20},
        )
        assert response1.status_code == 201
        assert response1.json()["id"] == 1

        response2 = client.post(
            "/api/users",
            json={"username": "user2", "age": 30},
        )
        assert response2.status_code == 201
        assert response2.json()["id"] == 2


class TestValidationEndpoint:
    """Тесты для эндпоинта валидации пользователя (Задание 10.2)."""

    def test_validate_user_success(self, client: TestClient):
        """Тест успешной валидации пользователя."""
        response = client.post(
            "/users/validate",
            json={
                "username": "testuser",
                "age": 25,
                "email": "test@example.com",
                "password": "securepass123",
                "phone": "+79001234567",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User data is valid"
        assert data["user"]["username"] == "testuser"

    def test_validate_user_invalid_age(self, client: TestClient):
        """Тест валидации с неверным возрастом."""
        response = client.post(
            "/users/validate",
            json={
                "username": "testuser",
                "age": 16,
                "email": "test@example.com",
                "password": "securepass123",
            },
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "ValidationError"
        assert "age" in data["message"]

    def test_validate_user_invalid_email(self, client: TestClient):
        """Тест валидации с неверным email."""
        response = client.post(
            "/users/validate",
            json={
                "username": "testuser",
                "age": 25,
                "email": "invalid-email",
                "password": "securepass123",
            },
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "ValidationError"
        assert "email" in data["message"]

    def test_validate_user_short_password(self, client: TestClient):
        """Тест валидации со слишком коротким паролем."""
        response = client.post(
            "/users/validate",
            json={
                "username": "testuser",
                "age": 25,
                "email": "test@example.com",
                "password": "short",
            },
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "ValidationError"
        assert "password" in data["message"]

    def test_validate_user_long_password(self, client: TestClient):
        """Тест валидации со слишком длинным паролем."""
        response = client.post(
            "/users/validate",
            json={
                "username": "testuser",
                "age": 25,
                "email": "test@example.com",
                "password": "this_password_is_way_too_long",
            },
        )
        assert response.status_code == 422
        data = response.json()
        assert data["error"] == "ValidationError"
        assert "password" in data["message"]

    def test_validate_user_default_phone(self, client: TestClient):
        """Тест валидации с значением телефона по умолчанию."""
        response = client.post(
            "/users/validate",
            json={
                "username": "testuser",
                "age": 25,
                "email": "test@example.com",
                "password": "securepass123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["phone"] == "Unknown"


class TestCustomExceptions:
    """Тесты для пользовательских исключений (Задание 10.1)."""

    def test_custom_exception_a(self, client: TestClient):
        """Тест CustomExceptionA."""
        response = client.get("/check-age?age=16")
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "CustomExceptionA"
        assert "Age must be at least 18" in data["message"]

    def test_custom_exception_a_success(self, client: TestClient):
        """Тест успешного прохождения CustomExceptionA."""
        response = client.get("/check-age?age=25")
        assert response.status_code == 200
        data = response.json()
        assert data["age"] == 25
        assert "valid" in data["message"]

    def test_custom_exception_b(self, client: TestClient):
        """Тест CustomExceptionB."""
        response = client.get("/resource/999")
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "CustomExceptionB"
        assert "not found" in data["message"]

    def test_custom_exception_b_success(self, client: TestClient):
        """Тест успешного получения ресурса."""
        response = client.get("/resource/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Test Resource"


class TestProductEndpoints:
    """Тесты для эндпоинтов продуктов (Задание 9.1)."""

    @pytest.mark.asyncio
    async def test_create_product(self, async_client, setup_database):
        """Тест создания продукта."""
        response = await async_client.post(
            "/products",
            json={
                "title": "Test Product",
                "price": 99.99,
                "count": 10,
                "description": "Test description",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Product"
        assert data["price"] == 99.99
        assert data["count"] == 10
        assert data["description"] == "Test description"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_product(self, async_client, setup_database):
        """Тест получения продукта."""
        create_response = await async_client.post(
            "/products",
            json={
                "title": "Test Product",
                "price": 99.99,
                "count": 10,
                "description": "Test description",
            },
        )
        product_id = create_response.json()["id"]

        response = await async_client.get(f"/products/{product_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["title"] == "Test Product"

    @pytest.mark.asyncio
    async def test_get_product_not_found(self, async_client, setup_database):
        """Тест получения несуществующего продукта."""
        response = await async_client.get("/products/999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_products(self, async_client, setup_database):
        """Тест получения списка продуктов."""
        await async_client.post(
            "/products",
            json={
                "title": "Product 1",
                "price": 10.0,
                "count": 5,
                "description": "Description 1",
            },
        )
        await async_client.post(
            "/products",
            json={
                "title": "Product 2",
                "price": 20.0,
                "count": 3,
                "description": "Description 2",
            },
        )

        response = await async_client.get("/products")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2