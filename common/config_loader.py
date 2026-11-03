"""
配置加载器：
  1. 读取 config/config.yaml；
  2. 根据环境变量 TEST_ENV 选择环境（dev / ci，默认 dev）；
  3. 合并 common 公共配置和当前环境配置；
  4. 用环境变量覆盖敏感字段（密码、地址等），CI 里不写死密码。

用法：
  from common.config_loader import get_config
  cfg = get_config()
  cfg.ruoyi.base_url   # 点访问
  cfg["ruoyi"]["base_url"]  # 字典访问
"""
import os
from pathlib import Path

import yaml

# 配置文件路径（本文件在 common/ 下，项目根目录是上两级）
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "config.yaml"


class AttrDict(dict):
    """支持点访问的字典：cfg.ruoyi.base_url 等价于 cfg['ruoyi']['base_url']"""

    def __getattr__(self, key):
        try:
            value = self[key]
        except KeyError:
            raise AttributeError(f"配置项不存在: {key}")
        # 嵌套字典也转成 AttrDict，支持连续点访问
        return AttrDict(value) if isinstance(value, dict) else value

    def __setattr__(self, key, value):
        self[key] = value


# 环境变量 -> 配置路径 的映射表
# key 是环境变量名，value 是覆盖到配置里的 (一级模块, 字段名)
_ENV_OVERRIDES = {
    "RUOYI_BASE_URL": ("ruoyi", "base_url"),
    "RUOYI_USERNAME": ("ruoyi", "username"),
    "RUOYI_PASSWORD": ("ruoyi", "password"),
    "SHOP_BASE_URL": ("shop", "base_url"),
    "SHOP_USERNAME": ("shop", "username"),
    "SHOP_PASSWORD": ("shop", "password"),
    "SHOP_PAY_SECRET": ("shop", "pay_secret"),  # 支付验签密钥，须与 shop_service 环境变量一致
    "MYSQL_HOST": ("mysql", "host"),
    "MYSQL_PORT": ("mysql", "port"),
    "MYSQL_USER": ("mysql", "user"),
    "MYSQL_PASSWORD": ("mysql", "password"),
    "REDIS_HOST": ("redis", "host"),
    "REDIS_PORT": ("redis", "port"),
    "REDIS_PASSWORD": ("redis", "password"),
    "REDIS_PROTOCOL": ("redis", "protocol"),
}

# 端口类环境变量需要转成整数
_INT_FIELDS = {("mysql", "port"), ("redis", "port"), ("redis", "protocol")}

_config = None


def load_config() -> AttrDict:
    """加载并合并配置（实际执行一次）"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    # 选择当前环境
    env_name = os.environ.get("TEST_ENV", raw.get("env", "dev"))
    if env_name not in raw["environments"]:
        raise ValueError(f"未知环境 {env_name}，可选: {list(raw['environments'].keys())}")

    # 合并：common 打底，再用当前环境覆盖
    merged = dict(raw.get("common", {}))
    merged.update(raw["environments"][env_name])
    merged["env"] = env_name

    cfg = AttrDict(merged)

    # 应用环境变量覆盖
    for env_key, (section, field) in _ENV_OVERRIDES.items():
        if env_key in os.environ:
            value = os.environ[env_key]
            if (section, field) in _INT_FIELDS:
                value = int(value)
            cfg[section][field] = value

    return cfg


def get_config() -> AttrDict:
    """获取配置单例（整个测试进程只加载一次）"""
    global _config
    if _config is None:
        _config = load_config()
    return _config
