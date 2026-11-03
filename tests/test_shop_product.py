"""
电商商品模块测试（10 个用例：6 正常 + 4 异常）。
覆盖：创建、详情、列表、修改、上下架、名称搜索 + 重名、价格非法、404、未登录。
"""
import pytest

from common.assertions import (
    assert_biz_fail,
    assert_biz_ok,
    assert_data,
    assert_data_has_fields,
    assert_db_count,
    assert_db_row,
    assert_http,
)
from common.data_factory import create_product


# ===== 正常路径 =====
@pytest.mark.regression
def test_create_product_success(shop_logged, db):
    """创建商品：三层断言全做"""
    resp = shop_logged.post("/api/products", json={
        "name": "auto_test_手机", "price": 3999.5, "stock": 100, "description": "测试手机"
    })
    assert_http(resp, 201)
    assert_biz_ok(resp)
    assert_data(resp, {"name": "auto_test_手机", "price": 3999.5, "stock": 100})
    assert_data_has_fields(resp, ["id", "create_time"])
    pid = resp.json()["data"]["id"]
    # 第三层：数据库落库
    assert_db_row(db, "shop_product", {"id": pid}, {"stock": 100, "status": 1})


@pytest.mark.regression
def test_get_product_detail(shop_logged):
    """查单个商品详情"""
    p = create_product(shop_logged)
    resp = shop_logged.get(f"/api/products/{p['id']}")
    assert_http(resp, 200)
    assert_biz_ok(resp)
    assert_data(resp, {"id": p["id"], "name": p["name"]})


@pytest.mark.regression
def test_list_products(shop_logged):
    """商品列表分页"""
    create_product(shop_logged)
    resp = shop_logged.get("/api/products", params={"page": 1, "page_size": 5})
    assert_http(resp, 200)
    assert_biz_ok(resp)
    body = resp.json()["data"]
    assert body["page"] == 1 and len(body["list"]) <= 5


@pytest.mark.regression
def test_update_product(shop_logged, db):
    """修改商品价格和库存"""
    p = create_product(shop_logged, price=100, stock=10)
    resp = shop_logged.put(f"/api/products/{p['id']}", json={"price": 88.8, "stock": 20})
    assert_http(resp, 200)
    assert_biz_ok(resp)
    assert_data(resp, {"price": 88.8, "stock": 20})
    # 第三层：DB 同步更新
    assert_db_row(db, "shop_product", {"id": p["id"]}, {"price": 88.8, "stock": 20})


@pytest.mark.regression
def test_change_product_status(shop_logged, db):
    """商品下架再上架"""
    p = create_product(shop_logged)
    # 下架
    r1 = shop_logged.put(f"/api/products/{p['id']}/status", json={"status": 0})
    assert_http(r1, 200)
    assert_biz_ok(r1)
    assert_db_row(db, "shop_product", {"id": p["id"]}, {"status": 0})
    # 上架
    r2 = shop_logged.put(f"/api/products/{p['id']}/status", json={"status": 1})
    assert_http(r2, 200)
    assert_db_row(db, "shop_product", {"id": p["id"]}, {"status": 1})


@pytest.mark.regression
def test_list_filter_by_name(shop_logged):
    """按名称模糊搜索"""
    create_product(shop_logged, name="auto_test_唯一关键词XYZ")
    resp = shop_logged.get("/api/products", params={"name": "唯一关键词XYZ"})
    assert_http(resp, 200)
    assert_biz_ok(resp)
    assert resp.json()["data"]["total"] >= 1


# ===== 异常路径 =====
@pytest.mark.regression
def test_create_duplicate_name(shop_logged, db):
    """重名商品：400 + DB 不新增"""
    create_product(shop_logged, name="auto_test_重名商品")
    before = db.query(
        "SELECT COUNT(*) c FROM shop_product WHERE name='auto_test_重名商品'"
    )[0]["c"]
    resp = shop_logged.post("/api/products", json={
        "name": "auto_test_重名商品", "price": 10, "stock": 1
    })
    assert_http(resp, 400)
    assert_biz_fail(resp, expected_msg="已存在")
    after = db.query(
        "SELECT COUNT(*) c FROM shop_product WHERE name='auto_test_重名商品'"
    )[0]["c"]
    assert after == before, "重名居然写库了"


@pytest.mark.regression
def test_create_price_negative(shop_logged, db):
    """价格为负数：Pydantic 校验 422，DB 无新增"""
    before = db.query("SELECT COUNT(*) c FROM shop_product")[0]["c"]
    resp = shop_logged.post("/api/products", json={
        "name": "auto_test_负价", "price": -5, "stock": 1
    })
    assert_http(resp, 422)
    after = db.query("SELECT COUNT(*) c FROM shop_product")[0]["c"]
    assert after == before, "非法价格居然写库了"


@pytest.mark.regression
def test_get_product_not_found(shop_logged):
    """查不存在的商品：404"""
    resp = shop_logged.get("/api/products/999999")
    assert_http(resp, 404)
    assert_biz_fail(resp)


@pytest.mark.regression
def test_unauthorized_access(shop_client):
    """不带 token 访问商品列表：401"""
    resp = shop_client.get("/api/products")
    assert_http(resp, 401)
