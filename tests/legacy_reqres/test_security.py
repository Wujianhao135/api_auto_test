

from common.assertions import assert_response

def test_sql_injection(api_client):
    """SQL安全注入测试"""
    payload = {"email": "' OR 1=1 --", "password": "anything"}
    resp = api_client.post("/login", json=payload)
    # 预期：应该返回 400 或 422，不能登录成功
    assert resp.status_code != 200, "SQL注入成功了！"


def test_xss_protection(api_client):
    """XSS防护测试：创建用户时输入脚本"""
    payload = {"name": "<script>alert(1)</script>", "job": "test"}
    resp = api_client.post("/users", json=payload)

    # 创建成功返回 201
    assert resp.status_code == 201

    # 检查返回的 name 里脚本是什么样的
    result = resp.json()
    print(f"返回的 name: {result['name']}")
    # ReqRes 会原样返回，真实系统应该转义成 &lt;script&gt;


def test_no_sensitive_info(api_client):
    """检查返回里有没有敏感信息"""
    resp = api_client.post("/login", json={
        "email": "eve.holt@reqres.in",
        "password": "cityslicka"
    })
    assert_response(resp, 200)
    result = resp.json()

    # 不能返回密码字段（用 not in，不是 in）
    assert "password" not in result, "返回里包含了密码！"