from server_app import Application
import logging
from match.service import MatchService
from status_points.match_status_enum import MatchStatus
from match.scoring_service.scoring import ScoringService
from match.controller import MatchController
from validator.validator import InputValidator
from jinja2 import Environment, FileSystemLoader, select_autoescape
from db.database import init_db
from pathlib import Path

def _templates_dir():
    return Path(__file__).parent.parent.resolve() / "frontend" / "templates"

def _static_dir():
    return Path(__file__).parent.parent.resolve() / "frontend" / "static"

def create_app():
    template_env: Environment = Environment(loader=FileSystemLoader(_templates_dir()),
                                       autoescape=select_autoescape(["html"]))
    template_env.globals["MatchStatus"] = MatchStatus
    static_dir = _static_dir()
    init_db()
    validator = InputValidator()
    scoreing_servicce = ScoringService()
    match_service = MatchService(scoreing_servicce)
    controller_match = MatchController(match_service, validator, template_env)
    app = Application(controller_match, template_env, static_dir)
    return app

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def app_start():
    app = create_app()
    try:
        logging.info("Запуск сервера...")
        app.run()
    except KeyboardInterrupt:
        logging.info("Сервер остановлен пользователем...")
    except SystemExit:
        logging.info("Программа завершает свою работу...")
    except Exception as err:
        logging.exception("Произошла непредвиденная ошибка: %s", err)
    finally:
        logging.info("Завершение соединения")

if __name__ == "__main__":
    app_start()