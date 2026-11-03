"""
三层断言体系（验收标准核心）：
  第一层 HTTP 状态码：assert_http()
  第二层 业务码 + 响应字段：assert_biz_ok() / assert_data()
  第三层 数据库状态：assert_db_row() / assert_db_count()

两个系统的成功响应结构一致：{code:200, msg, data}，所以业务码断言统一。
异常用例：若依 HTTP 也是 200 但 code 非 200；电商 FastAPI 直接 HTTP 4xx 且返回 {detail}。

用法示例（正常用例）：
  resp = shop_logged.post("/api/products", json={...})
  assert_http(resp, 201)
  assert_biz_ok(resp)
  assert_data(resp, {"name": "auto_test_x", "price": 100})
  assert_db_row(db, "shop_product", {"name": "auto_test_x"}, {"stock": 100})

异常用例：
  resp = shop_logged.post("/api/products", json={...})
  assert_http(resp, 400)
  assert_biz_fail(resp)
"""
from common.db_util import DBUtil


# ===== 第一层：HTTP 状态码 =====
def assert_http(resp, expected_status: int):
    """断言 HTTP 状态码"""
    assert resp is not None, "请求失败，返回了 None（服务可能未启动）"
    assert resp.status_code == expected_status, (
        f"HTTP 状态码不符：预期 {expected_status}，实际 {resp.status_code}，"
        f"响应体：{resp.text[:300]}"
    )


# ===== 第二层：业务码 + 响应字段 =====
def assert_biz_ok(resp):
    """断言业务成功：code == 200"""
    data = resp.json()
    assert data.get("code") == 200, (
        f"业务码不是 200：code={data.get('code')} msg={data.get('msg')}，"
        f"完整响应：{resp.text[:300]}"
    )


def assert_biz_fail(resp, expected_msg: str = None):
    """断言业务失败（异常用例用）：若依 code 非 200，或电商 HTTP 4xx 返回 detail"""
    # 电商 FastAPI 异常：HTTP 已经是 4xx/5xx，body 是 {"detail": ...}
    body = resp.json()
    if "code" in body:
        # 若依或电商业务异常，code 非 200
        assert body.get("code") != 200, (
            f"预期业务失败，但 code=200 成功了，响应：{resp.text[:300]}"
        )
        if expected_msg:
            assert expected_msg in body.get("msg", ""), (
                f"失败提示不符：预期含 '{expected_msg}'，实际 '{body.get('msg')}'"
            )
    else:
        # FastAPI 异常结构 {"detail": "..."}
        detail = body.get("detail", "")
        if expected_msg:
            assert expected_msg in str(detail), (
                f"失败提示不符：预期含 '{expected_msg}'，实际 '{detail}'"
            )


def assert_data(resp, expected: dict):
    """断言响应 data 里的字段值（第二层）"""
    body = resp.json()
    data = body.get("data", {})
    for field, expected_value in expected.items():
        actual = data.get(field)
        assert actual == expected_value, (
            f"字段 {field} 不符：预期 {expected_value}，实际 {actual}，"
            f"完整 data：{data}"
        )


def assert_data_has_fields(resp, fields: list):
    """断言响应 data 里包含这些字段（不查具体值）"""
    data = resp.json().get("data", {})
    for field in fields:
        assert field in data, f"data 里缺少字段 {field}，实际：{data}"


# ===== 第三层：数据库状态 =====
def assert_db_row(db: DBUtil, table: str, where: dict, expected: dict,
                  database: str = None):
    """
    断言数据库某一行的字段值。
    :param table: 表名
    :param where: 查询条件，如 {"name": "auto_test_x"}
    :param expected: 预期字段值，如 {"stock": 100, "status": 1}
    """
    where_sql = " AND ".join([f"{k}=%s" for k in where.keys()])
    rows = db.query(
        f"SELECT * FROM {table} WHERE {where_sql}",
        tuple(where.values()),
        database=database,
    )
    assert len(rows) == 1, (
        f"断言 {table} 条件 {where} 应查到 1 行，实际 {len(rows)} 行"
    )
    row = rows[0]
    for field, expected_value in expected.items():
        actual = row.get(field)
        # 数值类型宽松比较：Decimal("100.00") == 100 视为相等
        if isinstance(actual, (int, float)) or hasattr(actual, "__float__"):
            assert float(actual) == float(expected_value), (
                f"数据库 {table}.{field} 不符：预期 {expected_value}，实际 {actual}"
            )
        else:
            assert actual == expected_value, (
                f"数据库 {table}.{field} 不符：预期 {expected_value}，实际 {actual}"
            )


def assert_db_count(db: DBUtil, table: str, where: dict,
                     expected_count: int, database: str = None):
    """断言数据库某条件下的行数"""
    where_sql = " AND ".join([f"{k}=%s" for k in where.keys()])
    rows = db.query(
        f"SELECT COUNT(*) AS c FROM {table} WHERE {where_sql}",
        tuple(where.values()),
        database=database,
    )
    actual = rows[0]["c"]
    assert actual == expected_count, (
        f"表 {table} 条件 {where} 行数不符：预期 {expected_count}，实际 {actual}"
    )
