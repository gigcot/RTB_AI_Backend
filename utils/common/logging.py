import os
import logging
class Logger:
    def __init__(self, logger_name: str, log_level=logging.INFO):
        self.logger_name = logger_name

        # 기본 로그 디렉토리 설정
        base_dir = os.path.join(os.getcwd(), "output", "logs")
        os.makedirs(base_dir, exist_ok=True)
        log_file_path = os.path.join(base_dir, f"{logger_name}.log")

        # Logger 객체 생성
        self.__logger = logging.getLogger(logger_name)
        self.__logger.setLevel(log_level)

        # 기존 핸들러 제거 (중복 방지)
        self.__logger.handlers = []

        # 포맷 설정
        formatter = logging.Formatter(
            "[%(asctime)s] - %(levelname)s: %(message)s"
        )

        # 파일 핸들러 추가
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        self.__logger.addHandler(file_handler)

        # 콘솔 핸들러 추가
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.__logger.addHandler(console_handler)

    def get_logger(self) -> logging.Logger:
        return self.__logger