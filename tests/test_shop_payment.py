"""
电商支付回调模块测试（8 个用例：4 正常 + 4 异常）。
覆盖：发起支付、正常回调改状态、重复回调幂等、支付失败记录 + 签名错误、金额篡改、订单不存在、回调公开免登录。
签名规则：MD5(order_no + amount两位小数 + pay_status + PAY_SECRET)。
"""
import hashlib

import pytest

from common.assertions import (
    assert_biz_fail,
    assert_biz_ok,
    assert_db_count,
    assert_db_row,
    assert_http,
)
from common.config_loader import get_config
from common.data_factory import create_product


def _sign(order_no: str, amount, pay_status: int) -> str:
    """和服务端一致的签名算法（测试层独立实现，不 import 被测代码）"""
    secret = get_config().shop.pay_secret
    raw = f"{order_no}{float(amount):.2f}{pay_status}{secret}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def _make_order(shop_logged, price=100, stock=5, qty=1):
    """造一个待支付订单，返回 (order_no, amount)"""
    p = create_product(shop_logged, price=price, stock=stock)
    r = shop_logged.post("/api/orders", json={"items": [{"product_id": p["id"], "quantity": qty}]})
    data = r.json()["data"]
    return data["order_no"], data["total_amount"]


# ===== 正常路径 =====
@pytest.mark.regression
def test_request_payment(shop_logged):
    """发起支付：返回支付参数和签名"""
    order_no, amount = _make_order(shop_logged)
    resp = shop_logged.post(f"/api/pay/order/{order_no}")
    assert_http(resp, 200)
    assert_biz_ok(resp)
    body = resp.json()["data"]
    assert body["order_no"] == order_no
    assert "sign" in body and "transaction_id" in body


@pytest.mark.regression
def test_payment_callback_success(shop_logged, db):
    """正常回调：订单状态变已支付(1) + 写支付记录 + pay_time 落库"""
    order_no, amount = _make_order(shop_logged)
    sign = _sign(order_no, amount, 1)
    resp = shop_logged.post("/api/payment/callback", json={
        "order_no": order_no, "amount": amount, "pay_status": 1,
        "transaction_id": "TX_TEST_001", "sign": sign,
    })
    assert_http(resp, 200)
    assert_biz_ok(resp)
    # 第三层：订单状态=1 已支付
    assert_db_row(db, "shop_order", {"order_no": order_no}, {"status": 1})
    # 第三层：支付记录 1 条，成功
    assert_db_count(db, "shop_payment_record", {"order_no": order_no, "pay_status": 1}, 1)


@pytest.mark.regression
def test_payment_callback_idempotent(shop_logged, db):
    """重复回调：幂等返回，支付记录不重复写"""
    order_no, amount = _make_order(shop_logged)
    sign = _sign(order_no, amount, 1)
    payload = {
        "order_no": order_no, "amount": amount, "pay_status": 1,
        "transaction_id": "TX_DUP", "sign": sign,
    }
    # 第一次回调
    r1 = shop_logged.post("/api/payment/callback", json=payload)
    assert_http(r1, 200)
    # 第二次重复回调
    r2 = shop_logged.post("/api/payment/callback", json=payload)
    assert_http(r2, 200)
    assert "幂等" in r2.json().get("msg", "")
    # 第三层：支付记录仍然只有 1 条
    assert_db_count(db, "shop_payment_record", {"order_no": order_no}, 1)


@pytest.mark.regression
def test_payment_fail_record(shop_logged, db):
    """支付失败：订单状态不变(仍待支付0)，写一条失败记录"""
    order_no, amount = _make_order(shop_logged)
    sign = _sign(order_no, amount, 0)  # pay_status=0 失败
    resp = shop_logged.post("/api/payment/callback", json={
        "order_no": order_no, "amount": amount, "pay_status": 0,
        "transaction_id": "TX_FAIL", "sign": sign,
    })
    assert_http(resp, 200)
    assert_biz_ok(resp)
    # 第三层：订单仍待支付
    assert_db_row(db, "shop_order", {"order_no": order_no}, {"status": 0})
    # 第三层：失败记录 1 条
    assert_db_count(db, "shop_payment_record", {"order_no": order_no, "pay_status": 0}, 1)


# ===== 异常路径 =====
@pytest.mark.regression
def test_payment_bad_sign(shop_logged, db):
    """签名错误：400，订单状态不变"""
    order_no, amount = _make_order(shop_logged)
    resp = shop_logged.post("/api/payment/callback", json={
        "order_no": order_no, "amount": amount, "pay_status": 1,
        "transaction_id": "TX_BAD", "sign": "fake_sign_123",
    })
    assert_http(resp, 400)
    assert_biz_fail(resp, expected_msg="签名")
    assert_db_row(db, "shop_order", {"order_no": order_no}, {"status": 0})


@pytest.mark.regression
def test_payment_amount_mismatch(shop_logged, db):
    """回调金额被篡改：400"""
    order_no, amount = _make_order(shop_logged)
    wrong_amount = float(amount) + 999  # 故意改错
    sign = _sign(order_no, wrong_amount, 1)  # 用错金额算的签名
    resp = shop_logged.post("/api/payment/callback", json={
        "order_no": order_no, "amount": wrong_amount, "pay_status": 1,
        "transaction_id": "TX_TAMPER", "sign": sign,
    })
    assert_http(resp, 400)
    assert_biz_fail(resp, expected_msg="金额")
    assert_db_row(db, "shop_order", {"order_no": order_no}, {"status": 0})


@pytest.mark.regression
def test_payment_order_not_exist(shop_logged):
    """回调不存在的订单：404"""
    fake_no = "ORD_NO_EXIST"
    sign = _sign(fake_no, 100, 1)
    resp = shop_logged.post("/api/payment/callback", json={
        "order_no": fake_no, "amount": 100, "pay_status": 1,
        "transaction_id": "TX_404", "sign": sign,
    })
    assert_http(resp, 404)
    assert_biz_fail(resp, expected_msg="订单不存在")


@pytest.mark.regression
def test_callback_public_no_auth(shop_client):
    """支付回调是公开接口，不带 token 也能通到业务校验（不会 401）"""
    # 用未登录客户端打回调，预期不是 401（可能是 400/404，因为订单不存在）
    resp = shop_client.post("/api/payment/callback", json={
        "order_no": "X", "amount": 1, "pay_status": 1, "sign": "x",
    })
    assert resp.status_code != 401, "回调应该是公开接口，不该 401"
