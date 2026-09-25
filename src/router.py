from exceptions.base.domain_error import NotFoundError
from typing import Callable, Any
import re

class Router:
    def __init__(self):
        self.__endpoints: dict[str, dict[re.Pattern, Callable[..., Any]]] = {'GET': {}, 'POST': {}}

    def register(self, method: str, path: str, handler: str) -> None:
        self.__endpoints[method][re.compile(path)] = handler

    def resolve(self, path: str, method: str) -> tuple[Callable, dict[str, str | Any]]:
        for url, handler in self.__endpoints[method].items():
            match = url.fullmatch(path) #
            if match:
                return handler, match.groupdict()  
        raise NotFoundError()