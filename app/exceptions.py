"""Пользовательские исключения для задания 10.1."""

from fastapi import HTTPException, status


class CustomExceptionA(HTTPException):
    """Исключение для случая невыполнения бизнес-условия."""

    def __init__(self, detail: str = "Business condition not met"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "CustomExceptionA", "message": detail},
        )


class CustomExceptionB(HTTPException):
    """Исключение для случая, когда ресурс не найден."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "CustomExceptionB", "message": detail},
        )