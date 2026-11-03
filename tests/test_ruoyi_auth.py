"""
若依登录模块测试（5 个用例：2 正常 + 3 异常）。
若依登录流程：GET /captchaImage 拿 uuid → 从 Redis 读验证码答案 → POST /login。
若依特点：登录失败 HTTP 也是 200，靠 code 判断（失败 code=500）。
"""
import pytest

from common.assertions import (
    assert_biz_fail,
    assert_biz_ok,
    assert_http,
)
from common.redis_util import RedisUtil

# 整个文件的用例都标记为 ruoyi，CI 环境用 -m "not ruoyi" 跳过
pytestmark = pytest.mark.ruoyi


def _get_captcha(client):
    """获取验证码，返回 (uuid, 答案)"""
    r = client.get("/captchaImage")
    uuid = r.json()["uuid"]
    answer = RedisUtil().get_captcha_answer(uuid)
    return uuid, answer


@pytest.mark.regression
def test_ruoyi_login_success(ruoyi_client):
    """正常登录：返回 token，code=200"""
    uuid, answer = _get_captcha(ruoyi_client)
    resp = ruoyi_client.post("/login", json={
        "username": "admin", "password": "admin123",
        "code": answer, "uuid": uuid,
    })
    assert_http(resp, 200)
    assert_biz_ok(resp)
    assert "token" in resp.json()


@pytest.mark.regression
def test_ruoyi_get_info(ruoyi_logged):
    """获取当前用户信息：返回用户和权限"""
    resp = ruoyi_logged.get("/getInfo")
    assert_http(resp, 200)
    assert_biz_ok(resp)
    body = resp.json()
    assert body["user"]["userName"] == "admin"
    assert "roles" in body


@pytest.mark.regression
def test_ruoyi_login_wrong_password(ruoyi_client):
    """错误密码：code=500"""
    uuid, answer = _get_captcha(ruoyi_client)
    resp = ruoyi_client.post("/login", json={
        "username": "admin", "password": "wrong_password",
        "code": answer, "uuid": uuid,
    })
    assert_http(resp, 200)  # 若依登录失败 HTTP 也是 200
    assert_biz_fail(resp, expected_msg="密码错误")


@pytest.mark.regression
def test_ruoyi_login_wrong_captcha(ruoyi_client):
    """错误验证码：code=500"""
    uuid, _ = _get_captcha(ruoyi_client)
    resp = ruoyi_client.post("/login", json={
        "username": "admin", "password": "admin123",
        "code": "0000", "uuid": uuid,  # 故意错
    })
    assert_http(resp, 200)
    assert_biz_fail(resp, expected_msg="验证码")


@pytest.mark.regression
def test_ruoyi_login_empty_username(ruoyi_client):
    """空账号登录：code=500"""
    uuid, answer = _get_captcha(ruoyi_client)
    resp = ruoyi_client.post("/login", json={
        "username": "", "password": "admin123",
        "code": answer, "uuid": uuid,
    })
    assert_http(resp, 200)
    assert_biz_fail(resp)
