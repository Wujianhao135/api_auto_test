"""
FastAPI 电商服务入口。

启动方式（在项目根目录）：
  .venv\\Scripts\\python.exe -m uvicorn shop_service.main:app --host 0.0.0.0 --port 8000
文档地址：http://localhost:8000/docs
"""
from fastapi import FastAPI

from shop_service.routers import auth, order, payment, product

app = FastAPI(title="半真实电商服务", version="1.0.0")

# 挂载路由
app.include_router(auth.router)
app.include_router(product.router)
app.include_router(order.router)
app.include_router(payment.router)


@app.get("/health", tags=["健康检查"])
def health():
    """健康检查：CI 用来判断服务是否起来"""
    return {"code": 200, "msg": "服务正常", "data": None}
