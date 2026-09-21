import os
import sys

import pytest

# 把项目根目录加入路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.api_client import ApiClient


@pytest.fixture(scope="session")
def api_client():
    """
    整个测试会话只创建一个 ApiClient 实例
    scope="session"：所有用例共用同一个 client
    """
    client = ApiClient("config/config.yaml")
    yield client


@pytest.fixture(scope="session")
def login_token(api_client):
    """
    整个测试会话只登录一次，返回 token
    scope="session"：所有用例共用同一个 token
    """
    # 登录获取 token
    login_data = {"email": "eve.holt@reqres.in", "password": "cityslicka"}
    resp = api_client.post("/login", json=login_data)
    token = resp.json()["token"]

    # 把 token 设置到 client 里，后续请求自动带
    api_client.set_token(token)

    yield token

def test_get_users(api_client):
    resp = api_client.get("/users?page=1")
    assert resp.status_code == 200