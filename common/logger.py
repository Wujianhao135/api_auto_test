"""
日志工具：
  - 同时输出到控制台和日志文件；
  - 日志文件按日期命名（test_20261030.log），放在配置的 log_dir 下；
  - 统一格式：时间 | 文件名:行号 | 级别 | 消息；
  - 文件用 UTF-8 编码，避免中文乱码；
  - 单例控制，防止重复添加 handler 导致日志打印多遍。

用法：
  from common.logger import get_logger
  logger = get_logger(__name__)
  logger.info("这是一条日志")
"""
import logging
import time
from pathlib import Path

from common.config_loader import get_config

# 日志统一格式
_FORMAT = "%(asctime)s | %(filename)s:%(lineno)d | %(levelname)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 记录已配置过 handler 的 logger，避免重复
_configured = set()


def get_logger(name: str = "api_test") -> logging.Logger:
    """获取一个同时输出控制台和文件的 logger"""
    cfg = get_config()
    logger = logging.getLogger(name)

    # 已经配置过就直接返回，避免重复 handler
    if name in _configured:
        return logger

    logger.setLevel(cfg.log_level)
    logger.propagate = False  # 不向父 logger 传播，避免重复打印

    formatter = logging.Formatter(_FORMAT, datefmt=_DATE_FORMAT)

    # 1. 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. 文件 handler（按日期命名，UTF-8 编码）
    log_dir = Path(cfg.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"test_{time.strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    _configured.add(name)
    return logger
