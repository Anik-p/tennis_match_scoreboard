from core.server_app import Application
from core.app_init import AppInit
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

if __name__ == "__main__":
    initializer = AppInit()
    app = Application(initializer)
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