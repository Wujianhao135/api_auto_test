"""
数据库工具类：
  - 从配置读取 MySQL 连接参数；
  - query() 返回字典列表（方便按字段断言）；
  - execute() 执行增删改；
  - cleanup_test_data()：按外键依赖顺序清理 auto_test_ 测试数据。

用法：
  db = DBUtil()
  rows = db.query("SELECT * FROM shop_product WHERE name LIKE %s", ("auto_test_%",))
  db.execute("DELETE FROM shop_product WHERE name LIKE %s", ("auto_test_%",))
  db.cleanup_test_data()
"""
import pymysql

from common.config_loader import get_config
from common.logger import get_logger

# 测试数据统一前缀（AGENTS.md 规则 10）
TEST_PREFIX = "auto_test_"


class DBUtil:
    """MySQL 连接封装"""

    def __init__(self):
        cfg = get_config().mysql
        self.logger = get_logger("db_util")
        # 默认连电商库 shop，需要查若依库时用 db 参数指定
        self._default_db = cfg.shop_db
        self._conn_kwargs = dict(
            host=cfg.host,
            port=cfg.port,
            user=cfg.user,
            password=cfg.password,
            charset=cfg.charset,
            cursorclass=pymysql.cursors.DictCursor,
        )

    def _get_conn(self, database: str):
        kwargs = dict(self._conn_kwargs)
        kwargs["database"] = database
        return pymysql.connect(**kwargs)

    def query(self, sql: str, params=None, database: str = None) -> list[dict]:
        """查询，返回字典列表"""
        conn = self._get_conn(database or self._default_db)
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        finally:
            conn.close()

    def execute(self, sql: str, params=None, database: str = None) -> int:
        """增删改，返回受影响行数"""
        conn = self._get_conn(database or self._default_db)
        try:
            with conn.cursor() as cur:
                affected = cur.execute(sql, params)
            conn.commit()
            return affected
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def cleanup_test_data(self):
        """
        清理 shop 库所有 auto_test_ 前缀的测试数据。
        删除顺序必须遵守外键依赖：
          1. shop_order_item（引用订单和商品）
          2. shop_payment_record（引用订单）
          3. shop_order（引用用户）
          4. shop_product（商品）
          5. shop_user（测试用户）
        """
        prefix = TEST_PREFIX
        # 先找出测试用户的 id，后续按它删订单
        test_users = self.query(
            "SELECT id FROM shop_user WHERE username LIKE %s", (prefix + "%",)
        )
        user_ids = [u["id"] for u in test_users]

        deleted = {}

        if user_ids:
            placeholders = ",".join(["%s"] * len(user_ids))
            # 1. 订单项（这些用户的订单）
            deleted["order_item"] = self.execute(
                f"DELETE FROM shop_order_item WHERE order_id IN "
                f"(SELECT id FROM shop_order WHERE user_id IN ({placeholders}))",
                tuple(user_ids),
            )
            # 2. 支付记录
            deleted["payment_record"] = self.execute(
                "DELETE FROM shop_payment_record WHERE order_no IN "
                "(SELECT order_no FROM shop_order WHERE user_id IN (" + placeholders + "))",
                tuple(user_ids),
            )
            # 3. 订单
            deleted["order"] = self.execute(
                f"DELETE FROM shop_order WHERE user_id IN ({placeholders})",
                tuple(user_ids),
            )

        # 4. 商品（全部 auto_test_ 前缀，不按用户隔离）
        deleted["product"] = self.execute(
            "DELETE FROM shop_product WHERE name LIKE %s", (prefix + "%",)
        )
        # 5. 测试用户
        deleted["user"] = self.execute(
            "DELETE FROM shop_user WHERE username LIKE %s", (prefix + "%",)
        )

        self.logger.info(f"清理测试数据完成: {deleted}")
        return deleted

    def cleanup_ruoyi_test_users(self) -> int:
        """清理若依库 sys_user 表里的 auto_test_ 测试用户（ry-vue 库）。
        如果 ry-vue 库不存在（如 CI 环境），静默跳过，不报错。"""
        try:
            deleted = self.execute(
                "DELETE FROM sys_user WHERE user_name LIKE %s",
                (TEST_PREFIX + "%",),
                database="ry-vue",
            )
            self.logger.info(f"清理若依测试用户: {deleted} 条")
            return deleted
        except Exception as e:
            # CI 环境没有 ry-vue 库，跳过即可
            self.logger.warning(f"ry-vue 库不存在或清理失败，跳过: {e}")
            return 0
