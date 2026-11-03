"""
支付路由：发起支付 + 支付平台回调。

回调安全设计：
  1. 回调接口公开（支付平台无法带我们的 JWT），靠 MD5 签名验签；
  2. 签名规则：sign = MD5(order_no + amount + pay_status + secret)；
  3. 幂等：已支付订单重复回调，直接返回成功，不重复改状态、不重复写记录；
  4. 金额校验：回调金额必须等于订单金额，防止篡改。
"""
import hashlib
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from shop_service.common import success
from shop_service.config import PAY_SECRET
from shop_service.database import get_db
from shop_service.deps import get_current_user
from shop_service.models import Order, PaymentRecord, User
from shop_service.schemas import PaymentCallback

router = APIRouter(tags=["支付"])


def make_sign(order_no: str, amount, pay_status: int) -> str:
    """生成签名：MD5(订单号 + 金额 + 支付状态 + 密钥)
    金额统一格式化为两位小数，避免 Decimal(250.50) 和 float(250.5) 字符串不一致"""
    amount_str = f"{float(amount):.2f}"
    raw = f"{order_no}{amount_str}{pay_status}{PAY_SECRET}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


@router.post("/api/pay/order/{order_no}")
def request_payment(
    order_no: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """发起支付：校验订单后返回支付参数（含签名），模拟跳转到支付平台"""
    order = db.scalar(select(Order).where(Order.order_no == order_no))
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "订单不存在")
    if order.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "不能支付别人的订单")
    if order.status != 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "订单不是待支付状态")

    transaction_id = "TX" + uuid.uuid4().hex[:16]
    pay_status = 1
    sign = make_sign(order_no, order.total_amount, pay_status)

    return success({
        "order_no": order_no,
        "amount": float(order.total_amount),
        "pay_status": pay_status,
        "transaction_id": transaction_id,
        "sign": sign,
    }, "支付参数已生成")


@router.post("/api/payment/callback")
def payment_callback(body: PaymentCallback, db: Session = Depends(get_db)):
    """
    支付平台异步回调（公开接口，靠验签）。
    返回固定成功结构，支付平台收到非成功会重试。
    """
    # 1. 验签：重新计算签名和回调里的对比
    expected_sign = make_sign(body.order_no, body.amount, body.pay_status)
    if expected_sign != body.sign:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "签名校验失败")

    # 2. 查订单
    order = db.scalar(select(Order).where(Order.order_no == body.order_no))
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "订单不存在")

    # 3. 幂等：订单已支付，重复回调直接返回成功，不重复处理
    if order.status == 1:
        return success({"order_no": body.order_no}, "订单已处理，重复回调幂等返回")

    # 4. 金额校验：回调金额必须等于订单金额
    if float(body.amount) != float(order.total_amount):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "回调金额与订单金额不一致")

    # 5. 只有待支付订单能处理
    if order.status != 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "订单状态不允许支付")

    # 6. 支付失败：只写记录，不改订单状态
    if body.pay_status != 1:
        db.add(PaymentRecord(
            order_no=order.order_no,
            pay_amount=order.total_amount,
            pay_status=0,
            transaction_id=body.transaction_id,
        ))
        db.commit()
        return success({"order_no": order.order_no}, "支付失败已记录")

    # 7. 支付成功：改订单状态、记录支付时间、写支付记录
    order.status = 1
    order.pay_time = datetime.now()
    db.add(PaymentRecord(
        order_no=order.order_no,
        pay_amount=order.total_amount,
        pay_status=1,
        transaction_id=body.transaction_id,
    ))
    db.commit()
    return success({"order_no": order.order_no}, "支付成功")
