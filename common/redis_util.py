"""
Redis 工具类：
  - 从配置读取连接参数，封装连接（强制 RESP2 兼容老版本）；
  - 提供读取若依验证码答案的方法；
  - 也可用于后续校验 Redis 缓存数据。

用法：
  rcli = RedisUtil()
  code = rcli.get_captcha_answer(uuid)
"""
import json

import redis

from common.config_loader import get_config
from common.logger import get_logger


class RedisUtil:
    """Redis 连接封装"""

    def __init__(self):
        cfg = get_config().redis
        self.logger = get_logger("redis_util")
        # decode_responses 让返回值直接是 str，protocol=2 跳过 HELLO 握手
        self.client = redis.Redis(
            host=cfg.host,
            port=cfg.port,
            db=cfg.db,
            password=cfg.password,
            decode_responses=True,
            protocol=cfg.protocol,
        )
        # 初始化即验证连通，失败立即暴露
        self.client.ping()

    def get_captcha_answer(self, uuid: str) -> str:
        """
        读取若依验证码答案。
        若依把答案做了 JSON 序列化存 Redis（如 '"2"'），用 json.loads 去外层引号。
        """
        key = f"captcha_codes:{uuid}"
        raw = self.client.get(key)
        if raw is None:
            raise RuntimeError(f"Redis 中未找到验证码 {key}（可能已过期或 uuid 错误）")
        return json.loads(raw)

    def get(self, key: str):
        """读字符串值"""
        return self.client.get(key)

    def keys(self, pattern: str):
        """按模式查 key"""
        return self.client.keys(pattern)
