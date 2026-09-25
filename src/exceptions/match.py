from exceptions.app_error import AppErorr

class DataBaseValidatorError(AppErorr):
    def __init__(self, missing_file: str = None):
        self.status_code = 500
        message = "Нет данных для валидатора"
        if missing_file is not None:
            message += f"отсутсвует файл: '{missing_file}'"
        super().__init__(message)
        
class DatabaseOperationError(AppErorr):
    def __init__(self, operation: str):
        self.status_code = 500
        message = f"Ошибка операции БД: {operation}"
        super().__init__(message)

class MatchNotFoundError(AppErorr):
    def __init__(self):
        self.status_code = 404
        message = "База данных не содержит информации о текущем матче"
        super().__init__(message) 

class InvalidScoreTransitionError(AppErorr):
    def __init__(self, error: str | None=None):
        self.status_code = 400
        message = f"Неожиданная ошибка при расчете счета матча"
        if error is not None:
            message += f": {error}"
        super().__init__(message)