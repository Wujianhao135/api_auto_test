"""
pytest 全局 fixture 配置（重构版）。

fixture 体系：
  config              session 级，加载多环境配置
  ruoyi_client        session 级，若依客户端（未登录，用于测试公开接口/鉴权用例）
  shop_client         session 级，电商客户端（未登录）
  ruoyi_logged        session 级，已登录的若依客户端（自动带 token）
  shop_logged         session 级，已登录的电商客户端（自动带 token）

scope 说明：
  session 级在整个测试运行只创建/登录一次，复用连接和 token，速度快；
  需要隔离的场景在用例内自行新建客户端。
"""
import os
import sys

import pytest

# 把项目根目录加入 sys.path，保证从任意位置运行都能 import common
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.api_client import ApiClient
from common.auth import login_ruoyi, login_shop
from common.config_loader import get_config
from common.db_util import DBUtil


@pytest.fixture(scope="session", autouse=True)
def clean_test_data():
    """
    整个测试会话开始前自动清理：删掉上次可能残留的 auto_test_ 数据，
    保证每次都从干净状态开始（上次跑崩了也不影响这次）。
    """
    db = DBUtil()
    db.cleanup_test_data()
    db.cleanup_ruoyi_test_users()
    yield


@pytest.fixture(scope="session")
def config():
    """加载配置（整个会话一份）"""
    return get_config()


@pytest.fixture(scope="session")
def db():
    """数据库工具（session 级，用于三层断言的第三层）"""
    return DBUtil()


@pytest.fixture(scope="session")
def ruoyi_client(config):
    """若依客户端（未登录）"""
    return ApiClient(config.ruoyi.base_url, config.timeout)


@pytest.fixture(scope="session")
def shop_client(config):
    """电商客户端（未登录）"""
    return ApiClient(config.shop.base_url, config.timeout)


@pytest.fixture(scope="session")
def ruoyi_logged(config):
    """已登录的若依客户端：登录后自动带 token"""
    client = ApiClient(config.ruoyi.base_url, config.timeout)
    token = login_ruoyi(client, config.ruoyi.username, config.ruoyi.password)
    client.set_token(token)
    return client


@pytest.fixture(scope="session")
def shop_logged(config):
    """已登录的电商客户端：登录后自动带 token"""
    client = ApiClient(config.shop.base_url, config.timeout)
    token = login_shop(client, config.shop.username, config.shop.password)
    client.set_token(token)
    return client
