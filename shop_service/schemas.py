"""
Pydantic 模型：定义接口的请求体和响应体格式。
FastAPI 会自动校验类型，类型不对直接返回 422。
本文件先放登录相关，商品/订单在后续小步追加。
"""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求体"""
    username: str = Field(..., min_length=1, description="登录账号")
    password: str = Field(..., min_length=1, description="密码")


class TokenResponse(BaseModel):
    """登录成功返回的 token"""
    access_token: str
    token_type: str = "bearer"


# ===== 商品相关 =====
class ProductCreate(BaseModel):
    """新增商品请求体"""
    name: str = Field(..., min_length=1, max_length=100, description="商品名称")
    price: float = Field(..., gt=0, description="单价，必须大于 0")
    stock: int = Field(..., ge=0, description="库存，不能为负")
    description: str | None = Field(None, max_length=500)


class ProductUpdate(BaseModel):
    """修改商品请求体：字段都可选，只改传了的"""
    name: str | None = Field(None, min_length=1, max_length=100)
    price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    description: str | None = Field(None, max_length=500)


class ProductStatus(BaseModel):
    """上下架请求体"""
    status: int = Field(..., ge=0, le=1, description="1上架 0下架")


# ===== 订单相关 =====
class OrderItemRequest(BaseModel):
    """下单时的单个商品"""
    product_id: int = Field(..., ge=1)
    quantity: int = Field(..., ge=1, description="购买数量，至少 1 件")


class OrderCreate(BaseModel):
    """下单请求体"""
    items: list[OrderItemRequest] = Field(..., min_length=1)


# ===== 支付回调相关 =====
class PaymentCallback(BaseModel):
    """支付平台回调请求体"""
    order_no: str
    amount: float
    pay_status: int = Field(..., ge=0, le=1, description="1成功 0失败")
    transaction_id: str | None = None
    sign: str = Field(..., description="签名")
