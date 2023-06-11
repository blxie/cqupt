import os
import logging
from logging.handlers import RotatingFileHandler


class LogManager:
    # _instance = None

    # def __new__(cls):
    #     if cls._instance is None:
    #         cls._instance = super().__new__(cls)
    #     return cls._instance

    def __init__(self, log_path: str = "./app.log") -> None:
        self.log_path = log_path

    def initialize(self):
        log_dir = os.path.dirname(os.path.abspath(self.log_path))
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_max_size = 1024 * 128  # 最大日志文件大小（字节数）
        log_backup_count = 1  # 保留的备份文件数量

        handler = RotatingFileHandler(
            self.log_path, maxBytes=log_max_size, backupCount=log_backup_count, encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)  # 必须放在这里！即 self.logger.addHandler() 之前！
        logger.addHandler(handler)

        return logger
