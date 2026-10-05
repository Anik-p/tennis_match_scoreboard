from exceptions.app_error import AppError

class InvalidScoreTransitionError(AppError):
    def __init__(self, error: str | None=None):
        self.status_code = 400
        message = f"Неожиданная ошибка при расчете счета матча"
        if error is not None:
            message += f": {error}"
        super().__init__(message)

class NameNotFoundError(AppError):
    def __init__(self, base: str):
        self.status_code = 404
        message = f"Не удалось найти ник игрока: '{base}'"
        super().__init__(message)

class NotFoundError(AppError):
    def __init__(self, error: str | None):
        self.status_code = 404
        message = "Нет данных"
        if error is not None:
            message += f": {error}"
        super().__init__(message)

class NameNotFoundIdError(AppError):
    def __init__(self):
        self.status_code = 404
        message = f"Не удается найти идентификатор игрока"
        super().__init__(message)

class MatchNotFoundError(AppError):
    def __init__(self):
        self.status_code = 404
        message = "База данных не содержит информации о текущем матче"
        super().__init__(message) 

class AddNameError(AppError):
    def __init__(self, pl: str):
        self.status_code = 409
        message = f"Ник ('{pl}') уже существует"
        super().__init__(message)