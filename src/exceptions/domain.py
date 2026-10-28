from exceptions.base import NotFoundError, ConflictError, DomainError

class PlayerNotFoundError(NotFoundError):
    def __init__(self, nickname: str):
        super().__init__(f"Не удалось найти ник игрока: '{nickname}'")

class PlayerIdNotFoundError(NotFoundError):
    message = "Не удается найти идентификатор игрока"

class MatchNotFoundError(NotFoundError):
    message = "База данных не содержит информации о текущем матче"

class PlayerAlreadyExistsError(ConflictError):
    def __init__(self, nickname: str):
        super().__init__(f"Ник ('{nickname}') уже существует")

class InvalidScoreTransitionError(DomainError):
    def __init__(self, error: str | None = None):
        message = "Неожиданная ошибка при расчете счета матча"
        if error:
            message += f": {error}"
        super().__init__(message)