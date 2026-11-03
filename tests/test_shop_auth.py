"""
电商登录模块测试（4 个用例：2 正常 + 2 异常）。
电商登录：POST /api/auth/login，成功返回 JWT；失败 HTTP 401/403。
"""
import pytest

from common.assertions import (
    assert_biz_fail,
    assert_biz_ok,
    assert_data_has_fields,
    assert_http,
)
from common.data_factory import create_user


@pytest.mark.regression
def test_shop_login_success(shop_client):
    """正常登录：返回 access_token"""
    resp = shop_client.post("/api/auth/login", json={
        "username": "admin", "password": "admin123"
    })
    assert_http(resp, 200)
    assert_biz_ok(resp)
    assert_data_has_fields(resp, ["access_token", "token_type"])


@pytest.mark.regression
def test_shop_login_wrong_password(shop_client):
    """错误密码：401"""
    resp = shop_client.post("/api/auth/login", json={
        "username": "admin", "password": "wrong"
    })
    assert_http(resp, 401)
    assert_biz_fail(resp)


@pytest.mark.regression
def test_shop_login_user_not_exist(shop_client):
    """不存在用户：401"""
    resp = shop_client.post("/api/auth/login", json={
        "username": "no_such_user_xxx", "password": "123"
    })
    assert_http(resp, 401)
    assert_biz_fail(resp)


@pytest.mark.regression
def test_shop_login_inactive_user(shop_client, db):
    """停用账号登录：403"""
    u = create_user(db, status=0)  # status=0 停用
    resp = shop_client.post("/api/auth/login", json={
        "username": u["username"], "password": u["password"]
    })
    assert_http(resp, 403)
    assert_biz_fail(resp)
