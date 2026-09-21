from handler import Handler
from router import Router
from core.app_init import AppInit
from http.server import HTTPServer
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
INIT_HOST = os.getenv("API_HOST")
INIT_PORT = int(os.getenv("API_PORT"))

class Application:
    def __init__(self, initializer: AppInit):
        self.init = initializer
        self.router = Router()
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.register("GET", "/", self.init.controller_match.index)
        self.router.register("GET", "/new-match", self.init.controller_match.new_match_form)
        self.router.register("POST", "/new-match", self.init.controller_match.create_new_match)
        self.router.register("GET", "/match-score", self.init.controller_match.get_match_score)
        self.router.register("POST", "/match-score", self.init.controller_match.award_point)
        self.router.register("GET", "/matches", self.init.controller_match.get_matches)

    def _static_dir(self):
        return Path(__file__).parent.parent.parent.resolve() / "frontend" / "static"
    
    def create_request_handler(self, request, client_address, server):
        return Handler(
            request=request,
            client_address=client_address,
            server=server,
            router=self.router,
            static_dir=self._static_dir(),
            template_env=self.init.temlate_env
            )
    
    def run(self, host=INIT_HOST, port=INIT_PORT):
        server = HTTPServer((host, port), self.create_request_handler)
        print(f"Сервер запущен на {host}:{port}")
        server.serve_forever()