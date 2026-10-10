from urllib.parse import urlparse, parse_qs
from exceptions.app_error import AppError
from exceptions.base.domain_error import NotFoundError
from pathlib import Path
from jinja2 import Environment
from http.server import BaseHTTPRequestHandler
from typing import TYPE_CHECKING
import logging
import mimetypes

if TYPE_CHECKING:
    from session_fabric import SessionFabric
    from response import Response
    from router import Router

class Handler(BaseHTTPRequestHandler):
    """
    HTTP обработчик для REST API.
    
    Поддерживаемые методы:
    - GET: получение данных сыгранных и действующих матчей
    - POST: обновления табло матча
    """
    STATIC_PREFIXES = ("/css/", "/js/", "/images/")

    def __init__(self, 
                 request, 
                 client_address, 
                 server,
                 router: Router,
                 static_dir: Path,
                 template_env: Environment,
                 session_fabric: SessionFabric):

        self._static_dir = static_dir
        self._template_env = template_env
        self._router = router
        self._session_fabric = session_fabric
        super().__init__(request, client_address, server)

    def _handle(self, method: str):
        """
        Компоненты:
            - handler - экземпляр контроллера, полученный из router.resolve()
            - path_params - параметры запроса URL
            - query_params: параметры из строки запроса после '?'
            - params - объединенный словарь path_params + query_params
            - response - результат запроса handler(params)

        Обработка запросов:
            - Получение self.path от BaseHTTPRequestHandler
            - Разбиение self.path в self.router методом resolve, который возвращает (handler, path_params)
            - Инициализация params и добавление (если есть) в path_params
            - Получение query_params параметры запроса, если есть, добавляем в params
            - Вызываем handler(params) для получения response
            - Отправляем response в frontend через _send_response()

        Пример запроса:  
        ------------------------------------------------------------------------   
             POST /match-score?uuid=3fa85f64-5717-4562-b3fc-2c963f66afa6 HTTP/1.1

             Host: 127.0.0.1:8000

             Content-Type: application/x-www-form-urlencoded

             Content-Length: 11

             winner_id=5 
        ------------------------------------------------------------------------
        Пример успешной обработки:

        1. Разбор URI:

            urlparse(self.path)

            url_path = (scheme)://(netloc)/(path);(params)?(query)#(fragment)

            path = /match-score

            query_params = {"uuid": [3fa85f64-5717-4562-b3fc-2c963f66afa6]}

        2. Роутинг:

            handler = self._router.resolve(url_path.path, method=method)

            handler = self.controllers.award_point


        3. Сбор и распаковка параметров:     

            params = {}

            if query_params:
                query_params = {key: value[0] for key, value in query_params.items()}
                params.update({"uuid": 3fa85f64-5717-4562-b3fc-2c963f66afa6})
            
            if method == "POST":
                body_params = {"winner_id": 5}
                params.update({"winner_id": 5})

        4. Выполнение бизнес-логики:

            with self._session_fabric._create_match_service() as match_service:  
                
                Открытие сессии для запросов в БД с
                инициализацией репозиториев и сервиса матча.

                response = handler(params, match_service)
                 
                (response = self.controllers.award_point({"uuid": 3fa85f64-5717-4562-b3fc-2c963f66afa6, "winner_id": 5}, MatchService))

        5. Рендеринг ответа:

                self._send_response(response) - переадресация страницы Response от контроллера.            
        """
        try:
            url_path = urlparse(self.path)
            path = url_path.path
            if path.startswith(self.STATIC_PREFIXES):
                return self._serve_static(path)
            query_params = parse_qs(url_path.query) 
            handler = self._router.resolve(url_path.path, method=method) 
            params = {}
            if query_params: 
                query_params = {key: value[0] for key, value in query_params.items()} 
                params.update(query_params)
            if method == "POST":
                body_params = self.get_params()
                params.update(body_params)
            with self._session_fabric.create_match_service() as uow:
                response = handler(params, uow)
                self._send_response(response)
        except AppError as err:
            self._send_error_page(err.status_code, str(err))
        except Exception:
            logging.exception("Необработанная ошибка: %s %s", method, self.path)
            self._send_error_page(500, "Внутренняя ошибка сервера")       
        
    def _serve_static(self, path: str) -> None:
        """
        Отдача статических файлов (CSS, JS, изображения) из локальной директории.

        Пример выполнения: 

        path_temp = Path(path.lstrip("/")) - Получение названия статического файла

        if ".." in path_temp.parts: - Защита от обхода директории, останавливая запрос в вида
                                        GET /static/../../.env где '..' означает выход на один уровень
                                        вверх в коррень проекта в файлу .env.
        
            raise NotFoundError() - базовое исключение.

        file_path = self._static_dir / path_temp - Формирование абсолютного пути к файлу
                                                   путем склеивания пути базовой директории статики и названия файла.

        if not file_path.is_file(): - проверяем, что данный путь введет к файлу
        
            raise NotFoundError(f"Статический файл не найден: {path}")

        data = file_path.read_bytes() - Считываем файл в виде сырого бинарного потока байт.

        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream" 
        
            Функция mimetypes.guess_type(str(file_path)) принимает путь к файлу,
            смотрит на его расширение и возвращает кортеж из двух элементов: (MIME_type, encoding).
            Например:
                - Для style.css она вернет: ("text/css", None)
                - Для image.png она вернет: ("image/png", None)
                - Для script.js она вернет: ("application/javascript", None)

            or "application/octet-stream" - это сырой бинарный поток данных,
            благодяря чему запускает скачивание файла на компьютер пользователя, вместо открытия неизвестного файла.
            Это позволяет избежать 'Content-Type: None' в случаи неизвестного типа данных

            Главная функция данной строки: гарантировать, что польователь получит адекватный ответ без подброса
            исключения и случайным образом не считал файл с неизвестным форматом.
                                                                                                
        Формирование ответа:

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        Пример ответа:

            HTTP/1.1 200 OK
            Content-Type: text/css; charset=utf-8
            Content-Length: 1420
            Connection: close

            body {
                    font-family: sans-serif;
                    background-color: #f8f9fa;
                }

            (остальной код CSS)

        """
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
            - Читает заголовок Content-Length для определения размера данных
            - Читает тело запроса через self.rfile.read()
            - Декодирует байты в строку UTF-8
            - Парсит строку в словарь через parse_qs()
            - Преобразует значения из списков в строки (берет первый элемент)
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
            # Если сломался движок шаблонов или удален error.html,
            # отдаем сырой HTML, чтобы сервер не упал в бесконечную рекурсию.
        except Exception:
            body = f"<h1>Ошибка {status}</h1><p>{message}</p>"
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_response(self, response: Response) -> None:
         # Если в объекте ответа указан Location - выполняем HTTP 302 перенаправление
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