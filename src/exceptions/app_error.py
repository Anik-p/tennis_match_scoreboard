class ExchangeError(Exception):
    """Базовое исключение приложения"""
    status_code: int = 500
    def __init__(self, message: str):
        super().__init__(message)