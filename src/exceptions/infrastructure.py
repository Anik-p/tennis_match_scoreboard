from exceptions.base import AppError, InfrastructureError

class DatabaseUnavailableError(InfrastructureError):
    message = "База данных недоступна"

class DatabaseError(AppError):
    """Базовая ошибка для всех сбоев внутри БД (500)"""
    status_code: int = 500
    message = "Ошибка базы данных"

class DatabaseOperationError(DatabaseError):
    def __init__(self, operation: str):
        super().__init__(f"Ошибка при выполнении операции БД: {operation}")

class DatabaseValidatorError(DatabaseError):
    def __init__(self, missing_file: str | None = None):
        message = "Нет данных для валидатора"
        if missing_file:
            message += f". Отсутствует файл: '{missing_file}'"
        super().__init__(message)