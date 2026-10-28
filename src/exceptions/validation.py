from exceptions.base import ValidationError

class MissingRequiredFieldError(ValidationError):
    message = "Обязательное поле формы не заполнено"

class IncorrectInputNameError(ValidationError):
    def __init__(self, params: str | None = None):
        message = "Данный ввод ника не корректен"
        if params:
            message += f": {params}"
        super().__init__(message)