import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from repopilot.utils.path_tool import get_abs_path, get_module_name


LOG_ROOT = Path(get_abs_path("logs"))
LOG_ROOT.mkdir(parents=True, exist_ok=True)

DEFAULT_LOG_FORMAT = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
)


def get_logger(
    name: str = get_module_name(__file__),
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    log_file: str | Path | None = None,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if logger.handlers:
        return logger

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(console_handler)

    if log_file is None:
        log_file = LOG_ROOT / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    else:
        log_file = Path(log_file)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(file_handler)

    return logger


logger = get_logger()


if __name__ == "__main__":
    logger.info("信息日志")
    logger.warning("警告日志")
    logger.error("错误日志")
    logger.debug("调试日志")
    logger.critical("严重日志")
