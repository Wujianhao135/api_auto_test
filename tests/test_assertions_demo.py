"""
阶段 5 演示：三层断言体系怎么用。
这个文件是阶段 6 正式用例的模板，保留作参考。
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


@pytest.mark.smoke
def test_create_product_three_layers(shop_logged, db):
    """正常创建商品：三层断言全做"""
    # 造数据（商品名由工厂自动加前缀）
    payload = {"name": "auto_test_demo", "price": 99.5, "stock": 10}

    # 第一二层：HTTP + 业务码 + 响应字段
    resp = shop_logged.post("/api/products", json=payload)
    assert_http(resp, 201)
    assert_biz_ok(resp)
    assert_data(resp, {"name": "auto_test_demo", "price": 99.5, "stock": 10})
    product_id = resp.json()["data"]["id"]

    # 第三层：数据库真的写进去了，字段值正确
    assert_db_row(
        db, "shop_product",
        {"id": product_id},
        {"name": "auto_test_demo", "price": 99.5, "stock": 10, "status": 1},
    )


@pytest.mark.smoke
def test_create_duplicate_product_exception(shop_logged, db):
    """重名商品异常：HTTP 400 + 业务失败 + DB 没新增"""
    # 先造一个
    create_product(shop_logged, name="auto_test_dup", price=10, stock=5)
    before = db.query("SELECT COUNT(*) c FROM shop_product WHERE name='auto_test_dup'")[0]["c"]

    # 再创建重名
    resp = shop_logged.post("/api/products", json={"name": "auto_test_dup", "price": 1, "stock": 1})
    assert_http(resp, 400)
    assert_biz_fail(resp)

    # 第三层：DB 行数没增加
    after = db.query("SELECT COUNT(*) c FROM shop_product WHERE name='auto_test_dup'")[0]["c"]
    assert after == before, f"重名创建居然写库了：before={before} after={after}"


@pytest.mark.smoke
def test_order_deduct_stock(shop_logged, db):
    """下单三层断言：HTTP 成功 + DB 库存扣减 + DB 订单状态待支付"""
    # 造商品（库存 10）
    product = create_product(shop_logged, price=50, stock=10)

    # 下单买 3 件
    resp = shop_logged.post(
        "/api/orders",
        json={"items": [{"product_id": product["id"], "quantity": 3}]},
    )
    assert_http(resp, 201)
    assert_biz_ok(resp)
    order_no = resp.json()["data"]["order_no"]

    # 第三层 a：商品库存从 10 扣到 7
    assert_db_row(db, "shop_product", {"id": product["id"]}, {"stock": 7})
    # 第三层 b：订单是待支付状态（0）
    order_id = resp.json()["data"]["id"]
    assert_db_row(db, "shop_order", {"id": order_id}, {"status": 0})
    # 第三层 c：订单项数量正确（order_item 通过 order_id 关联）
    assert_db_count(db, "shop_order_item", {"order_id": order_id, "quantity": 3}, 1)
