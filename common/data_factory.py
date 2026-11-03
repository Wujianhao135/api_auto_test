"""
数据工厂：测试需要什么数据就现场造，自动带 auto_test_ 前缀。
  - create_product：通过 API 创建商品（商品 CRUD 本身就是被测接口）；
  - create_user：电商服务没有注册接口，直接用 DB 插入测试用户（bcrypt 哈希密码）。

造出来的数据由 cleanup_test_data() 统一清理，用例不用自己删。

用法：
  product = create_product(shop_logged, price=99.5, stock=10)
  user = create_user(db)  # 返回 {id, username}
"""
import uuid

import bcrypt

from common.api_client import ApiClient
from common.db_util import DBUtil, TEST_PREFIX
from common.logger import get_logger

logger = get_logger("data_factory")


def _unique(suffix: str) -> str:
    """生成唯一的测试名：auto_test_<suffix>_<8位随机>"""
    return f"{TEST_PREFIX}{suffix}_{uuid.uuid4().hex[:8]}"


def create_product(client: ApiClient, name: str = None,
                   price: float = 100.0, stock: int = 100,
                   status: int = 1, description: str = "自动化测试商品") -> dict:
    """
    通过 API 创建一个测试商品。
    :return: 商品字典（含 id, name, price, stock, status）
    """
    name = name or _unique("product")
    resp = client.post("/api/products", json={
        "name": name,
        "price": price,
        "stock": stock,
        "description": description,
    })
    data = resp.json()
    if data.get("code") != 201 and resp.status_code not in (200, 201):
        raise RuntimeError(f"创建商品失败: {resp.status_code} {resp.text}")
    product = data["data"]
    # 如果指定下架，再调状态接口
    if status == 0:
        client.put(f"/api/products/{product['id']}/status", json={"status": 0})
        product["status"] = 0
    logger.info(f"造商品: id={product['id']} name={product['name']}")
    return product


def create_user(db: DBUtil, username: str = None,
                 password: str = "test123456", status: int = 1) -> dict:
    """
    直接用 DB 插入一个测试用户（电商服务无注册接口）。
    :return: {id, username}
    """
    username = username or _unique("user")
    # bcrypt 哈希密码，和 shop_service 保持一致
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user_id = db.execute(
        "INSERT INTO shop_user (username, password, status) VALUES (%s, %s, %s)",
        (username, hashed, status),
    )
    logger.info(f"造用户: id={user_id} username={username}")
    return {"id": user_id, "username": username, "password": password}
