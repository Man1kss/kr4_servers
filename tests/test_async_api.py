"""Асинхронные модульные тесты с использованием Faker (Задание 11.2)."""

import pytest
from httpx import AsyncClient
from faker import Faker


class TestAsyncUserEndpoints:
    """Асинхронные тесты для эндпоинтов работы с пользователями."""

    @pytest.mark.asyncio
    async def test_create_user_async(self, async_client: AsyncClient, faker: Faker):
        """Тест создания пользователя с данными от Faker."""
        username = faker.user_name()
        age = faker.random_int(min=19, max=65)

        response = await async_client.post(
            "/api/users",
            json={"username": username, "age": age},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == username
        assert data["age"] == age
        assert data["id"] == 1

    @pytest.mark.asyncio
    async def test_get_user_async(self, async_client: AsyncClient, faker: Faker):
        """Тест получения пользователя."""
        username = faker.user_name()
        age = faker.random_int(min=19, max=65)

        create_response = await async_client.post(
            "/api/users",
            json={"username": username, "age": age},
        )
        user_id = create_response.json()["id"]

        response = await async_client.get(f"/api/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == username
        assert data["age"] == age

    @pytest.mark.asyncio
    async def test_get_nonexistent_user_async(self, async_client: AsyncClient):
        """Тест получения несуществующего пользователя."""
        response = await async_client.get("/api/users/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    @pytest.mark.asyncio
    async def test_delete_user_async(self, async_client: AsyncClient, faker: Faker):
        """Тест удаления пользователя."""
        create_response = await async_client.post(
            "/api/users",
            json={
                "username": faker.user_name(),
                "age": faker.random_int(min=19, max=65),
            },
        )
        user_id = create_response.json()["id"]

        delete_response = await async_client.delete(f"/api/users/{user_id}")
        assert delete_response.status_code == 204

        get_response = await async_client.get(f"/api/users/{user_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_nonexistent_user_async(self, async_client: AsyncClient):
        """Тест удаления несуществующего пользователя."""
        response = await async_client.delete("/api/users/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    @pytest.mark.asyncio
    async def test_create_user_invalid_age_async(
        self, async_client: AsyncClient, faker: Faker
    ):
        """Тест создания пользователя с невалидным возрастом."""
        response = await async_client.post(
            "/api/users",
            json={
                "username": faker.user_name(),
                "age": 16,
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_multiple_users_async(
        self, async_client: AsyncClient, faker: Faker
    ):
        """Тест создания нескольких пользователей с изоляцией состояния."""
        for i in range(3):
            response = await async_client.post(
                "/api/users",
                json={
                    "username": faker.user_name(),
                    "age": faker.random_int(min=19, max=65),
                },
            )
            assert response.status_code == 201
            assert response.json()["id"] == i + 1

    @pytest.mark.asyncio
    async def test_boundary_age_values_async(self, async_client: AsyncClient, faker: Faker):
        """Тест граничных значений возраста."""
        response = await async_client.post(
            "/api/users",
            json={"username": faker.user_name(), "age": 19},
        )
        assert response.status_code == 201

        response = await async_client.post(
            "/api/users",
            json={"username": faker.user_name(), "age": 120},
        )
        assert response.status_code == 201


class TestAsyncValidationEndpoint:
    """Асинхронные тесты для эндпоинта валидации с Faker."""

    @pytest.mark.asyncio
    async def test_validate_user_with_faker_async(
        self, async_client: AsyncClient, faker: Faker
    ):
        """Тест валидации пользователя с данными от Faker."""
        response = await async_client.post(
            "/users/validate",
            json={
                "username": faker.user_name(),
                "age": faker.random_int(min=19, max=80),
                "email": faker.email(),
                "password": faker.password(length=12),
                "phone": faker.phone_number(),
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User data is valid"

    @pytest.mark.asyncio
    async def test_validate_user_boundary_age_async(
        self, async_client: AsyncClient, faker: Faker
    ):
        """Тест граничных значений возраста при валидации."""
        response = await async_client.post(
            "/users/validate",
            json={
                "username": faker.user_name(),
                "age": 19,
                "email": faker.email(),
                "password": faker.password(length=10),
            },
        )
        assert response.status_code == 200

        response = await async_client.post(
            "/users/validate",
            json={
                "username": faker.user_name(),
                "age": 18,
                "email": faker.email(),
                "password": faker.password(length=10),
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_validate_user_password_boundaries_async(
        self, async_client: AsyncClient, faker: Faker
    ):
        """Тест граничных значений длины пароля."""
        response = await async_client.post(
            "/users/validate",
            json={
                "username": faker.user_name(),
                "age": 25,
                "email": faker.email(),
                "password": "a" * 8,
            },
        )
        assert response.status_code == 200

        response = await async_client.post(
            "/users/validate",
            json={
                "username": faker.user_name(),
                "age": 25,
                "email": faker.email(),
                "password": "a" * 16,
            },
        )
        assert response.status_code == 200

        response = await async_client.post(
            "/users/validate",
            json={
                "username": faker.user_name(),
                "age": 25,
                "email": faker.email(),
                "password": "a" * 7,
            },
        )
        assert response.status_code == 422

        response = await async_client.post(
            "/users/validate",
            json={
                "username": faker.user_name(),
                "age": 25,
                "email": faker.email(),
                "password": "a" * 17,
            },
        )
        assert response.status_code == 422


class TestAsyncCustomExceptions:
    """Асинхронные тесты для пользовательских исключений."""

    @pytest.mark.asyncio
    async def test_custom_exception_a_boundary_async(self, async_client: AsyncClient):
        """Тест граничных значений для CustomExceptionA."""
        response = await async_client.get("/check-age?age=17")
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "CustomExceptionA"

        response = await async_client.get("/check-age?age=18")
        assert response.status_code == 200
        data = response.json()
        assert data["age"] == 18

    @pytest.mark.asyncio
    async def test_custom_exception_b_multiple_async(self, async_client: AsyncClient):
        """Тест множественных запросов к ресурсу."""
        for resource_id in [2, 3, 100, 999]:
            response = await async_client.get(f"/resource/{resource_id}")
            assert response.status_code == 404
            data = response.json()
            assert data["error"] == "CustomExceptionB"

        response = await async_client.get("/resource/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1


class TestHealthEndpoint:
    """Тесты для эндпоинта проверки здоровья."""

    @pytest.mark.asyncio
    async def test_health_check_async(self, async_client: AsyncClient):
        """Тест проверки работоспособности."""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"