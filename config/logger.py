# import os
# import logging


# LOG_DIRS = {
#     "db_logs": "logs/db_logs",
#     "api_logs": "logs/api_logs"
# }

# for path in LOG_DIRS.values():
#     os.makedirs(path, exist_ok=True)
# class CustomFormatter(logging.Formatter):
#     def format(self, record):
#         return super().format(record)

# formatter = CustomFormatter(
#     "%(asctime)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s"
# )

# def setup_logger(name, log_file, level=logging.INFO):
#     """Функция для настройки отдельного логгера"""
#     logger = logging.getLogger(name)
#     logger.setLevel(level)

#     # Создаём обработчик записи в файл
#     file_handler = logging.FileHandler(log_file)
#     file_handler.setFormatter(formatter)

#     # Добавляем обработчик к логгеру
#     logger.addHandler(file_handler)

#     return logger

# # Логгер для БД
# db_logger = setup_logger('db_logger', f"{LOG_DIRS['db_logs']}/db.log")
# db_error_logger = setup_logger('db_error_logger', f"{LOG_DIRS['db_logs']}/errors.log", logging.ERROR)

# # Логгер для API
# api_logger = setup_logger('api_logger', f"{LOG_DIRS['api_logs']}/requests.log")
# api_error_logger = setup_logger('api_error_logger', f"{LOG_DIRS['api_logs']}/errors.log", logging.ERROR)