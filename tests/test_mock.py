from unittest.mock import Mock, patch
import pytest
from common.api_client import ApiClient


# ========== 被测业务函数 ==========
def get_user_name(api_client, user_id):
    """
    业务函数：根据用户ID获取用户名
    如果接口失败，返回"未知用户"
    """
    resp = api_client.get(f"/users/{user_id}")

    if resp is None:
        return "未知用户"

    if resp.status_code == 200:
        return resp.json()["data"]["first_name"]

    return "未知用户"


# ========== Mock 测试用例 ==========

@patch("common.api_client.ApiClient.get")
def test_get_user_name_success(mock_get):
    """测试1：接口正常返回200，应该返回用户名"""
    # Mock 一个假的响应
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {"id": 2, "first_name": "Janet"}
    }
    mock_get.return_value = mock_resp

    # 调用业务函数
    client = ApiClient("config/config.yaml")
    result = get_user_name(client, 2)

    # 断言
    assert result == "Janet"
    # 验证 get 方法确实被调用了，参数是 /users/2
    mock_get.assert_called_once_with("/users/2")


@patch("common.api_client.ApiClient.get")
def test_get_user_name_not_found(mock_get):
    """测试2：接口返回404，应该返回"未知用户" """
    mock_resp = Mock()
    mock_resp.status_code = 404
    mock_get.return_value = mock_resp

    client = ApiClient("config/config.yaml")
    result = get_user_name(client, 999)

    assert result == "未知用户"


@patch("common.api_client.ApiClient.get")
def test_get_user_name_timeout(mock_get):
    """测试3：接口超时返回None，应该返回"未知用户" """
    mock_get.return_value = None  # 模拟请求失败

    client = ApiClient("config/config.yaml")
    result = get_user_name(client, 1)

    assert result == "未知用户"
