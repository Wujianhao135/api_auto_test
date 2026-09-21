import os
import sys

import pytest

# 把项目根目录加入路径，让 tests 能 import common
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.api_client import ApiClient

# 登录测试数据（参数化）
login_data = [
    ("正常登录", {"email": "eve.holt@reqres.in", "password": "cityslicka"}, 200, "token"),
    ("空邮箱", {"email": "", "password": "cityslicka"}, 400, "error"),
    ("空密码", {"email": "eve.holt@reqres.in", "password": ""}, 400, "error"),
    ("缺少密码字段", {"email": "eve.holt@reqres.in"}, 400, "error"),
]



@pytest.mark.parametrize("desc, payload, expected_code, expected_field", login_data)
def test_login(desc, payload, expected_code, expected_field):
    """
    登录测试：参数化4组数据
    :param desc: 测试场景描述
    :param payload: 请求数据
    :param expected_code: 预期状态码
    :param expected_field: 预期返回的字段
    """
    # 初始化客户端
    client = ApiClient("config/config.yaml")

    # 发登录请求
    resp = client.post("/login", json=payload)

    # 断言：响应不能是 None
    assert resp is not None, f"{desc}: 请求失败，返回 None"

    # 断言：状态码符合预期
    assert resp.status_code == expected_code, \
        f"{desc}: 预期状态码 {expected_code}, 实际 {resp.status_code}"

    # 断言：返回字段存在
    result = resp.json()
    assert expected_field in result, \
        f"{desc}: 返回中没有字段 {expected_field}, 返回内容: {result}"
