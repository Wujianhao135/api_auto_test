import pytest


# ========== 创建用户 ==========
@pytest.mark.parametrize("name, job, expected_code", [
    ("morpheus", "leader", 201),
    ("neo", "developer", 201),
    ("trinity", "engineer", 201),
])
def test_create_user(api_client, name, job, expected_code):
    """
    创建用户测试
    :param api_client: conftest 里的 fixture
    :param name: 用户名
    :param job: 职业
    :param expected_code: 预期状态码
    """
    payload = {"name": name, "job": job}
    resp = api_client.post("/users", json=payload)

    assert resp is not None
    assert resp.status_code == expected_code

    result = resp.json()
    assert result["name"] == name
    assert result["job"] == job
    assert "id" in result


# ========== 查用户列表 ==========
def test_get_user_list(api_client):
    """查用户列表"""
    resp = api_client.get("/users?page=1")

    assert resp.status_code == 200
    result = resp.json()
    assert "data" in result
    assert len(result["data"]) > 0


# ========== 查单个用户 ==========
@pytest.mark.parametrize("user_id, expected_code", [
    (2, 200),
    (999, 404),
])
def test_get_user_detail(api_client, user_id, expected_code):
    """查单个用户详情"""
    resp = api_client.get(f"/users/{user_id}")

    assert resp.status_code == expected_code

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
    assert delete_resp.status_code == 204
