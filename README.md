# Контрольная работа №4

**Технологии разработки серверных приложений**

FastAPI приложение с миграциями Alembic, пользовательской обработкой ошибок, валидацией данных и модульными тестами.

## Требования

- Python 3.10 или выше (рекомендуется 3.13)
- pip
- SQLite (встроен в Python)

## Установка и запуск

### 1. Клонирование репозитория

git clone <url-репозитория>
cd fastapi-kr4

### 2. Создание виртуального окружения

Windows:
python -m venv venv
.\venv\Scripts\Activate.ps1

Linux/macOS:
python3 -m venv venv
source venv/bin/activate

### 3. Установка зависимостей

pip install -r requirements.txt

### 4. Настройка базы данных

Важно: приложение работает с базой данных в корне проекта (fastapi-kr4/app.db).

Скопируйте базу данных из папки app в корень проекта:

Windows:
copy app\app.db app.db

Linux/macOS:
cp app/app.db app.db

Если базы данных ещё нет, создайте её:

cd app
alembic upgrade head
copy app.db ..\app.db
cd ..

### 5. Запуск приложения

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

После запуска приложение доступно по адресу: http://127.0.0.1:8000

Примечание: файл .env не требуется, приложение работает с настройками по умолчанию.

## Проверка функциональности

### Документация API

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Проверка здоровья: http://127.0.0.1:8000/health

### Основные сценарии проверки

#### 1. Создание продукта (Задание 9.1)

Через Swagger UI:
- Открыть http://127.0.0.1:8000/docs
- Найти POST /products
- Нажать "Try it out"
- Вставить JSON:
{
  "title": "Ноутбук",
  "price": 999.99,
  "count": 5,
  "description": "Игровой ноутбук"
}
- Нажать "Execute"
- Ожидаемый ответ: 201 Created

#### 2. Получение продукта

- GET /products/{product_id}
- Ввести ID = 1
- Ожидаемый ответ: 200 OK с данными продукта

#### 3. Проверка пользовательских исключений (Задание 10.1)

- GET /check-age?age=16 -> 400 Bad Request (CustomExceptionA)
- GET /check-age?age=25 -> 200 OK
- GET /resource/999 -> 404 Not Found (CustomExceptionB)
- GET /resource/1 -> 200 OK

#### 4. Валидация данных пользователя (Задание 10.2)

- POST /users/validate
- Валидные данные:
{
  "username": "testuser",
  "age": 25,
  "email": "test@example.com",
  "password": "securepass123"
}
- Ожидаемый ответ: 200 OK
- Невалидные данные (age=16, неверный email, короткий пароль) -> 422 Validation Error

#### 5. In-memory API пользователей (Задания 11.1, 11.2)

- POST /api/users с телом {"username": "user", "age": 25} -> 201 Created
- GET /api/users/1 -> 200 OK
- DELETE /api/users/1 -> 204 No Content
- GET /api/users/1 -> 404 Not Found

## Тестирование

### Запуск всех тестов

pytest -v

### Запуск отдельных групп тестов

pytest tests/test_api.py -v
pytest tests/test_async_api.py -v
pytest tests/test_api.py::TestCustomExceptions -v
pytest tests/test_api.py::TestValidationEndpoint -v

### Ожидаемый результат

35 passed in 0.39s

## Структура проекта

fastapi-kr4/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── exceptions.py
│   ├── alembic.ini
│   ├── app.db
│   └── migrations/
│       ├── env.py
│       ├── script.py.mako
│       └── versions/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api.py
│   └── test_async_api.py
├── app.db
├── .gitignore
├── requirements.txt
└── README.md

## Важные замечания

- База данных app.db должна находиться в корне проекта (fastapi-kr4/app.db)
- При применении миграций через Alembic база создается в папке app, её нужно скопировать в корень
- Файл .env не используется, приложение работает с путём по умолчанию sqlite+aiosqlite:///./app.db
- Тесты используют in-memory SQLite и не влияют на основную базу данных

## API Endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | /products | Создание продукта |
| GET | /products/{id} | Получение продукта |
| GET | /products | Список продуктов |
| GET | /check-age | Проверка возраста |
| GET | /resource/{id} | Получение ресурса |
| POST | /users/validate | Валидация пользователя |
| POST | /api/users | Создание пользователя |
| GET | /api/users/{id} | Получение пользователя |
| DELETE | /api/users/{id} | Удаление пользователя |
| GET | /health | Проверка здоровья |

## Устранение неполадок

### Ошибка "no such table: products"

cd app
alembic upgrade head
copy app.db ..\app.db
cd ..

### Ошибка "ModuleNotFoundError: No module named 'app'"

Убедитесь, что запускаете сервер из корня проекта (fastapi-kr4), а не из папки app.

### Ошибка кодировки в .env

Файл .env не требуется для работы приложения. Если он есть и вызывает ошибку, удалите его.