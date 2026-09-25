from handler import Handler
from router import Router
from http.server import HTTPServer
from pathlib import Path
import os
from dotenv import load_dotenv
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from match.controller import MatchController

load_dotenv()
INIT_HOST = os.getenv("API_HOST")
INIT_PORT = int(os.getenv("API_PORT"))

class Application:
    def __init__(self,
                 controllers: MatchController,
                 temlate_env,
                 static_dir):
        self.controllers = controllers
        self.temlate_env = temlate_env
        self.static_dir = static_dir
        self.router = Router()
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.register("GET", "/", self.controllers.index)
        self.router.register("GET", "/new-match", self.controllers.new_match_form)
        self.router.register("POST", "/new-match", self.controllers.create_new_match)
        self.router.register("GET", "/match-score", self.controllers.get_match_score)
        self.router.register("POST", "/match-score", self.controllers.award_point)
        self.router.register("GET", "/matches", self.controllers.get_matches)

    def _static_dir(self):
        return Path(__file__).parent.parent.parent.resolve() / "frontend" / "static"
    
    def create_request_handler(self, request, client_address, server):
        return Handler(
            request=request,
            client_address=client_address,
            server=server,
            router=self.router,
            static_dir=self.static_dir,
            template_env=self.temlate_env
            )
    
    def run(self, host=INIT_HOST, port=INIT_PORT):
        server = HTTPServer((host, port), self.create_request_handler)
        print(f"Сервер запущен на {host}:{port}")
        server.serve_forever()