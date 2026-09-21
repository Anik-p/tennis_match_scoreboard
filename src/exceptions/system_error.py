from exceptions.app_error import ExchangeError

class DatabaseUnavailableError(ExchangeError):
    def __init__(self, error: str | None=None):
        self.status_code = 503
        message = "База данных недоступна"
        if error is not None:
            message += f": {error}"
        super().__init__(message)

class DatabaseOperationError(ExchangeError):
    def __init__(self, operation: str):
        self.status_code = 500
        message = f"Ошибка операции БД: {operation}"
        super().__init__(message)

class NameNotFoundIdError(ExchangeError):
    def __init__(self):
        self.status_code = 404
        message = f"Нет данных игрока"
        super().__init__(message)