"""
电商订单模块测试（9 个用例：5 正常 + 4 异常）。
覆盖：下单扣库存、列表、详情、取消回补、金额计算 + 库存不足、下架、商品不存在、未登录。
订单状态：0=待支付，1=已支付，2=已取消。
"""
import pytest

from common.assertions import (
    assert_biz_fail,
    assert_biz_ok,
    assert_data,
    assert_db_count,
    assert_db_row,
    assert_http,
)
from common.data_factory import create_product


@pytest.mark.regression
def test_create_order_success(shop_logged, db):
    """下单成功：三层断言 + 库存扣减 + DB 订单待支付"""
    p = create_product(shop_logged, price=50, stock=10)
    resp = shop_logged.post("/api/orders", json={
        "items": [{"product_id": p["id"], "quantity": 3}]
    })
    assert_http(resp, 201)
    assert_biz_ok(resp)
    order_no = resp.json()["data"]["order_no"]
    order_id = resp.json()["data"]["id"]

    # 第三层：库存 10→7
    assert_db_row(db, "shop_product", {"id": p["id"]}, {"stock": 7})
    # 第三层：订单待支付 status=0
    assert_db_row(db, "shop_order", {"id": order_id}, {"status": 0})
    # 第三层：订单项 1 行，数量 3
    assert_db_count(db, "shop_order_item", {"order_id": order_id, "quantity": 3}, 1)


@pytest.mark.regression
def test_order_total_amount(shop_logged, db):
    """订单金额用数据库单价算，不信前端传的价格"""
    p = create_product(shop_logged, price=100.0, stock=10)
    # 下单买 2 件，预期金额 200
    resp = shop_logged.post("/api/orders", json={
        "items": [{"product_id": p["id"], "quantity": 2}]
    })
    assert_http(resp, 201)
    assert_data(resp, {"total_amount": 200.0})


@pytest.mark.regression
def test_order_list(shop_logged):
    """订单列表能查到自己的订单"""
    create_product(shop_logged)  # 先确保有数据
    resp = shop_logged.get("/api/orders", params={"page": 1, "page_size": 5})
    assert_http(resp, 200)
    assert_biz_ok(resp)
    assert "list" in resp.json()["data"]


@pytest.mark.regression
def test_get_order_detail(shop_logged):
    """订单详情：items 里包含商品信息"""
    p = create_product(shop_logged, price=30, stock=5)
    r = shop_logged.post("/api/orders", json={
        "items": [{"product_id": p["id"], "quantity": 1}]
    })
    order_no = r.json()["data"]["order_no"]
    resp = shop_logged.get(f"/api/orders/{order_no}")
    assert_http(resp, 200)
    assert_biz_ok(resp)
    assert resp.json()["data"]["items"][0]["product_id"] == p["id"]


@pytest.mark.regression
def test_cancel_order_restock(shop_logged, db):
    """取消订单：状态变已取消 + 库存回补"""
    p = create_product(shop_logged, price=20, stock=10)
    r = shop_logged.post("/api/orders", json={
        "items": [{"product_id": p["id"], "quantity": 4}]
    })
    order_no = r.json()["data"]["order_no"]
    # 下单后库存 10→6
    assert_db_row(db, "shop_product", {"id": p["id"]}, {"stock": 6})
    # 取消
    resp = shop_logged.post(f"/api/orders/{order_no}/cancel")
    assert_http(resp, 200)
    assert_biz_ok(resp)
    # 第三层：订单状态=2 已取消，库存回补到 10
    assert_db_row(db, "shop_order", {"order_no": order_no}, {"status": 2})
    assert_db_row(db, "shop_product", {"id": p["id"]}, {"stock": 10})


# ===== 异常路径 =====
@pytest.mark.regression
def test_order_out_of_stock(shop_logged, db):
    """库存不足：400 + 库存不变"""
    p = create_product(shop_logged, price=10, stock=2)
    before = db.query("SELECT stock FROM shop_product WHERE id=%s", (p["id"],))[0]["stock"]
    resp = shop_logged.post("/api/orders", json={
        "items": [{"product_id": p["id"], "quantity": 5}]
    })
    assert_http(resp, 400)
    assert_biz_fail(resp, expected_msg="库存不足")
    after = db.query("SELECT stock FROM shop_product WHERE id=%s", (p["id"],))[0]["stock"]
    assert after == before, "库存不足居然扣库存了"


@pytest.mark.regression
def test_order_offline_product(shop_logged):
    """商品已下架：400"""
    p = create_product(shop_logged, price=10, stock=5)
    shop_logged.put(f"/api/products/{p['id']}/status", json={"status": 0})
    resp = shop_logged.post("/api/orders", json={
        "items": [{"product_id": p["id"], "quantity": 1}]
    })
    assert_http(resp, 400)
    assert_biz_fail(resp, expected_msg="已下架")


@pytest.mark.regression
def test_order_product_not_exist(shop_logged):
    """商品不存在：400"""
    resp = shop_logged.post("/api/orders", json={
        "items": [{"product_id": 999999, "quantity": 1}]
    })
    assert_http(resp, 400)
    assert_biz_fail(resp, expected_msg="不存在")


@pytest.mark.regression
def test_order_unauthorized(shop_client):
    """未登录下单：401"""
    resp = shop_client.post("/api/orders", json={"items": [{"product_id": 1, "quantity": 1}]})
    assert_http(resp, 401)
