from exceptions.app_error import AppError

class IncorrectData(AppError):
    def __init__(self):
        self.status_code = 400
        message = "Обязательное поле формы не заполнено"
        super().__init__(message)

class IncorrectInputName(AppError):
    def __init__(self, params: str=None):
        self.status_code = 400
        message = "Данный ввод ника не корректен"
        if params is not None:
            message += f": {params}"
        super().__init__(message)

class DataBaseValidatorError(AppError):
    def __init__(self, missing_file: str = None):
        self.status_code = 500
        message = "Нет данных для валидатора"
        if missing_file is not None:
            message += f"отсутсвует файл: '{missing_file}'"
        super().__init__(message)