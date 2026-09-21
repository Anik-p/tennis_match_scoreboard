from urllib.parse import urlparse, parse_qs
from exceptions.app_error import ExchangeError
from exceptions.domain_error import NotFoundError
from exceptions.app_error import ExchangeError
from pathlib import Path
from jinja2 import Environment
from http.server import BaseHTTPRequestHandler
from typing import TYPE_CHECKING
import logging
import mimetypes

if TYPE_CHECKING:
    from response import Response
    from router import Router

class Handler(BaseHTTPRequestHandler):
    """
    HTTP обработчик для REST API.
    
    Поддерживаемые методы:
    - GET: получение данных сыгранных и действующих матчей
    - POST: обновления табло матча
    
    Формат ответов:

    """
    STATIC_PREFIXES = ("/css/", "/js/", "/images/")

    def __init__(self, 
                 request, 
                 client_address, 
                 server,
                 router: Router,
                 static_dir: Path,
                 template_env: Environment):

        self._static_dir = static_dir
        self._template_env = template_env
        self._router = router
        super().__init__(request, client_address, server)

    def _handle(self, method: str):
        """
        Компоненты:
        -handler - экземпляр контроллера, полученный из router.resolve()
        -path_params - параметры запроса URL
        -query_params: параметры из строки запроса после '?'
        -params - объединенный словарь path_params + query_params
        -response - результат запроса handler(params)

        Обработка запросов:
        -Получение self.path от BaseHTTPRequestHandler
        -Разбиение self.path в self.router методом resolve, который возвращает (handler, path_params)
        -Инициализация params и добавление (если есть) в path_params
        -Получение query_params параметры запроса, если есть, добавляем в params
        -Вызываем handler(params) для получения response
        -Отправляем response в frontend через _send_response()

        POST /match-score?uuid=3fa85f64-5717-4562-b3fc-2c963f66afa6 HTTP/1.1
        Host: 127.0.0.1:8000
        Content-Type: application/x-www-form-urlencoded
        Content-Length: 11

        winner_id=5 

        urlparse(self.path)
        <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
        """
        try:
            url_path = urlparse(self.path) #<scheme>://<netloc>/<path>;<params>?<query>#<fragment>
            path = url_path.path
            if path.startswith(self.STATIC_PREFIXES):
                return self._serve_static(path)
            
            query_params = parse_qs(url_path.query) #{uuid=[3fa85f64-5717-4562-b3fc-2c963f66afa6]} query-параметры (?uuid=..., ?page=..., ?filter_by_player_name=...)
            handler, path_params = self._router.resolve(url_path.path, method=method) #handler, {}
            params = {}
            if path_params:
                params.update(path_params)
            if query_params: 
                query_params = {key: value[0] for key, value in query_params.items()} #{uuid=3fa85f64-5717-4562-b3fc-2c963f66afa6}
                params.update(query_params)
            if method == "POST":
                body_params = self.get_params()
                params.update(body_params)    
            response = handler(params)
            self._send_response(response)
        except ExchangeError as err:
            self._send_error_page(err.status_code, str(err))
        except Exception:
            logging.exception("Необработанная ошибка: %s %s", method, self.path)
            self._send_error_page(500, "Внутренняя ошибка сервера")       
        
    def _serve_static(self, path: str) -> None:
        path_temp = Path(path.lstrip("/"))
        if ".." in path_temp.parts:
            raise NotFoundError()
        file_path = self._static_dir / path_temp
        if not file_path.is_file():
            raise NotFoundError(f"Статический файл не найден: {path}")
        data = file_path.read_bytes()
        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        return self._handle("GET")
    
    def do_POST(self):
        return self._handle("POST")

    def get_params(self) -> dict[str, str]:
        """
        Извлекает параметры из тела POST запроса.

        Обработка запросов:
        -Читает заголовок Content-Length для определения размера данных
        -Читает тело запроса через self.rfile.read()
        -Декодирует байты в строку UTF-8
        -Парсит строку в словарь через parse_qs()
        -Преобразует значения из списков в строки (берет первый элемент)
        """
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        params = parse_qs(post_data.decode('utf-8'))
        params = {key: value[0] for key, value in params.items()}
        return params

    def _send_error_page(self, status: int, message: str) -> None:
        try:
            body = self._template_env.get_template("error.html").render(
                status=status, message=message)
        except Exception:
            body = f"<h1>Ошибка {status}</h1><p>{message}</p>"
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_response(self, response: Response) -> None:
        if response.location:
            self.send_response(302)
            self.send_header("Location", response.location)
            self.end_headers()
            return
        data = response.body.encode("utf-8")
        self.send_response(response.status)
        self.send_header("Content-Type", response.content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        
    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Requested-With")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()