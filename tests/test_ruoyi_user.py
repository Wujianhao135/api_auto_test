"""
若依用户管理模块测试（7 个用例：4 正常 + 3 异常）。
覆盖：用户列表、新增、修改、查详情 + 重复用户名、缺字段、不存在用户。
新增用户用 auto_test_ 前缀，结束后由 cleanup_ruoyi_test_users 自动清理。
"""
import uuid

import pytest

from common.assertions import (
    assert_biz_fail,
    assert_biz_ok,
    assert_http,
)

# 整个文件的用例都标记为 ruoyi，CI 环境用 -m "not ruoyi" 跳过
pytestmark = pytest.mark.ruoyi


def _new_user_payload():
    """造一个若依新增用户请求体（手机号唯一，避免若依手机号唯一校验）"""
    uname = f"auto_test_{uuid.uuid4().hex[:8]}"
    phone = f"13{uuid.uuid4().int % 1000000000:08d}"  # 13 开头随机 11 位
    return {
        "userName": uname,
        "nickName": "自动化测试",
        "password": "Test123456",
        "deptId": 103,  # 研发部门
        "email": f"{uname}@test.com",
        "phonenumber": phone,
    }, uname


@pytest.mark.regression
def test_ruoyi_user_list(ruoyi_logged):
    """用户列表查询"""
    resp = ruoyi_logged.get("/system/user/list", params={"pageNum": 1, "pageSize": 5})
    assert_http(resp, 200)
    assert_biz_ok(resp)
    body = resp.json()
    assert "rows" in body and "total" in body


@pytest.mark.regression
def test_ruoyi_create_and_get_user(ruoyi_logged, db):
    """新增用户 + DB 验证落库"""
    payload, uname = _new_user_payload()
    resp = ruoyi_logged.post("/system/user", json=payload)
    assert_http(resp, 200)
    assert_biz_ok(resp)
    # 第三层：若依库 sys_user 里真有这个用户
    row = db.query(
        "SELECT user_name, status FROM sys_user WHERE user_name=%s",
        (uname,), database="ry-vue",
    )
    assert len(row) == 1, f"若依库没找到用户 {uname}"
    assert row[0]["user_name"] == uname


@pytest.mark.regression
def test_ruoyi_update_user(ruoyi_logged, db):
    """修改用户昵称"""
    payload, uname = _new_user_payload()
    ruoyi_logged.post("/system/user", json=payload)
    # 查到 userId
    user = db.query(
        "SELECT user_id FROM sys_user WHERE user_name=%s", (uname,), database="ry-vue"
    )[0]
    uid = user["user_id"]
    # 修改（若依要求带 userName）
    resp = ruoyi_logged.put("/system/user", json={
        "userId": uid, "userName": uname, "nickName": "改名后的昵称", "deptId": 103,
    })
    assert_http(resp, 200)
    assert_biz_ok(resp)
    # DB 验证
    row = db.query(
        "SELECT nick_name FROM sys_user WHERE user_id=%s", (uid,), database="ry-vue"
    )[0]
    assert row["nick_name"] == "改名后的昵称"


@pytest.mark.regression
def test_ruoyi_get_user_detail(ruoyi_logged, db):
    """查单个用户详情"""
    payload, uname = _new_user_payload()
    ruoyi_logged.post("/system/user", json=payload)
    user = db.query(
        "SELECT user_id FROM sys_user WHERE user_name=%s", (uname,), database="ry-vue"
    )[0]
    resp = ruoyi_logged.get(f"/system/user/{user['user_id']}")
    assert_http(resp, 200)
    assert_biz_ok(resp)


# ===== 异常路径 =====
@pytest.mark.regression
def test_ruoyi_create_duplicate_user(ruoyi_logged):
    """重复用户名：code=500"""
    payload, uname = _new_user_payload()
    ruoyi_logged.post("/system/user", json=payload)  # 第一次
    resp = ruoyi_logged.post("/system/user", json=payload)  # 第二次
    assert_http(resp, 200)
    assert_biz_fail(resp)


@pytest.mark.regression
def test_ruoyi_create_empty_username(ruoyi_logged):
    """空账号名新增：code=500"""
    payload, _ = _new_user_payload()
    payload["userName"] = ""
    resp = ruoyi_logged.post("/system/user", json=payload)
    assert_http(resp, 200)
    assert_biz_fail(resp)


@pytest.mark.regression
def test_ruoyi_get_user_not_found(ruoyi_logged):
    """查不存在的用户：HTTP 500 或业务失败"""
    resp = ruoyi_logged.get("/system/user/999999")
    # 若依对不存在用户通常返回 500 或错误页，这里断言不是 200 成功即可
    assert resp.status_code in (200, 500)
    if resp.status_code == 200:
        assert_biz_fail(resp)
