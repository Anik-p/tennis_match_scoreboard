from exceptions.app_error import AppError

class DatabaseOperationError(AppError):
    def __init__(self, operation: str):
        self.status_code = 500
        message = f"Ошибка операции БД: {operation}"
        super().__init__(message)