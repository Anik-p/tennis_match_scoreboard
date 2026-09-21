from match.match_controller import MatchController
from match.match_service import MatchService
from match.match_repository import MatchRepository
from match.scoring_service import ScoringService
from player.player_repository import PlayerRepository
from validator.validator import InputValidator
from jinja2 import Environment, FileSystemLoader, select_autoescape
from db.database import init_db
from pathlib import Path

class AppInit:
    def __init__(self):
        self.temlate_env: Environment = Environment(loader=FileSystemLoader(self.templates_dir()),
                                                    autoescape=select_autoescape(["html"]))
        self.app_core()

    def templates_dir(self):
        return Path(__file__).parent.parent.parent.resolve() / "frontend" / "templates"

    def app_core(self):
        self._init_db()
        self._init_repo()
        self._init_service()
        self._init_controller()

    def _init_db(self):
        self.session = init_db()

    def _init_repo(self):
        self.repo_player = PlayerRepository(self.session)
        self.repo_match = MatchRepository(self.session)

    def _init_service(self):
        score_service = ScoringService()
        self.service_match = MatchService(score_service,
                                         self.repo_match,
                                         self.repo_player)

    def _init_controller(self):
        validator = InputValidator()
        self.controller_match = MatchController(self.service_match, validator, self.temlate_env)
