from server_app import Application
import logging
from match.controller import MatchController
from match.session_fabric import SessionFabric
from validator.validator import InputValidator
from jinja2 import Environment, FileSystemLoader, select_autoescape
from db.database import init_db
from pathlib import Path

def _templates_dir():
    return Path(__file__).parent.parent.resolve() / "frontend" / "templates"

def _static_dir():
    return Path(__file__).parent.parent.resolve() / "frontend" / "static"

def create_app():
    temlate_env: Environment = Environment(loader=FileSystemLoader(_templates_dir()),
                                       autoescape=select_autoescape(["html"]))
    static_dir = _static_dir()
    init_db()
    session_fabric = SessionFabric()
    validator = InputValidator()
    controller_match = MatchController(validator, temlate_env, session_fabric)
    app = Application(controller_match, temlate_env, static_dir)
    return app

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
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