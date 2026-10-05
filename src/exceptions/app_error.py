class AppError(Exception):
    """Базовое исключение приложения"""
    status_code: int = 500
    def __init__(self, message: str):
        super().__init__(message)

class DomainError(AppError):
    """Ошибка бизнес логики"""
    status_code: int = 400

class InfrastuctureError(AppError):
    """Ошибка инфраструктуры (БД, сеть)"""
    status_code: int = 503

class ValidatationError(AppError):
    """Ошибка валидации входных данных"""
    status_code: int = 400