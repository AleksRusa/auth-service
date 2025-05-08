import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# class CustomFormatter(logging.Formatter):
#     def format(self, record):
#         return super().format(record)

# formatter = CustomFormatter(
#     "%(asctime)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s"
# )

# def setup_logger(name, level=logging.INFO):
#     """Функция для настройки отдельного логгера с выводом в stdout"""
#     logger = logging.getLogger(name)
#     logger.setLevel(level)

#     # Создаём обработчик вывода в stdout
#     stdout_handler = logging.StreamHandler(sys.stdout)
#     stdout_handler.setFormatter(formatter)

#     # Добавляем обработчик к логгеру
#     logger.addHandler(stdout_handler)
#     return logger

# logger = setup_logger('logger')