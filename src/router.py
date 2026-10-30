from exceptions import NotFoundError
from typing import Callable, Any

class Router:
    def __init__(self):
        self.__endpoints: dict[str, dict[str, Callable[..., Any]]] = {'GET': {}, 'POST': {}}

    def register(self, method: str, path: str, handler: Callable) -> None:
        self.__endpoints[method][path] = handler

    def resolve(self, path: str, method: str) -> Callable:
        try:
            return self.__endpoints[method][path]
        except KeyError:
            raise NotFoundError()