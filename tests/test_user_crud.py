import pytest
import os
import yaml
from common.assertions import assert_response


# 读取用户测试数据
data_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "user_data.yaml"
)
with open(data_path, encoding="utf-8") as f:
    user_data = yaml.safe_load(f)

# ========== 创建用户 ==========
@pytest.mark.parametrize("case",user_data["create_user"],ids=lambda x:x["title"])
def test_create_user(api_client, case):

    resp = api_client.post("/users", json=case["payload"])

    assert_response(resp, case["expected_code"], case["expected_fields"])


# ========== 查用户列表 ==========
def test_get_user_list(api_client):
    """查用户列表"""
    resp = api_client.get("/users?page=1")

    assert_response(resp, 200, ["data"])


# ========== 查单个用户 ==========
@pytest.mark.parametrize("user_id, expected_code", [
    (2, 200),
    (999, 404),
])
def test_get_user_detail(api_client, user_id, expected_code):
    """查单个用户详情"""
    resp = api_client.get(f"/users/{user_id}")

    assert_response(resp, expected_code)

    if expected_code == 200:
        result = resp.json()
        assert result["data"]["id"] == user_id


# ========== 删除用户 ==========
def test_delete_user(api_client):
    """删除用户（先创建一个，再删除）"""
    # 第一步：先创建一个用户
    create_payload = {"name": "test_delete", "job": "tester"}
    create_resp = api_client.post("/users", json=create_payload)
    user_id = create_resp.json()["id"]

    # 第二步：删除这个用户
    delete_resp = api_client.delete(f"/users/{user_id}")
    assert_response(delete_resp, 204)
