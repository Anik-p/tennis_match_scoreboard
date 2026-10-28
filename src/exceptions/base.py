class AppError(Exception):
    """Базовое исключение приложения"""
    status_code: int = 500
    message: str = "Внутренняя ошибка сервера"

    def __init__(self,
                  message: str | None = None,
                  details: str | None = None):
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)

class ValidationError(AppError):
    """Ошибки валидации входных данных (400)"""
    status_code: int = 400
    message: str = "Некорректные входные данные"

class DomainError(AppError):
    """Ошибки бизнес-логики (Общий случай 400, или индивидуальные)"""
    status_code: int = 400

class NotFoundError(DomainError):
    """Ресурс не найден (404)"""
    status_code: int = 404
    message: str = "Ресурс не найден"

class ConflictError(DomainError):
    """Конфликт состояния, дубликаты (409)"""
    status_code: int = 409

class InfrastructureError(AppError):
    """Ошибки внешних систем и инфраструктуры (503 / 500)"""
    status_code: int = 503
    message: str = "Сервис временно недоступен"