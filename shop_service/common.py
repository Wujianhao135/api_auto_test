"""
统一响应格式：和若依 AjaxResult 风格一致，方便测试断言业务码。
成功：{"code": 200, "msg": "操作成功", "data": {...}}
失败：{"code": 500, "msg": "错误信息", "data": null}
"""
from typing import Any


def success(data: Any = None, msg: str = "操作成功") -> dict:
    """成功响应"""
    return {"code": 200, "msg": msg, "data": data}


def fail(msg: str = "操作失败", code: int = 500) -> dict:
    """失败响应"""
    return {"code": code, "msg": msg, "data": None}
