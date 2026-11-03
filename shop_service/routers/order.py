"""
订单路由：创建订单、查询、取消。
创建订单是核心：校验商品和库存 → 计算金额 → 扣库存 → 写订单，全部在一个事务里。
"""
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from shop_service.common import success
from shop_service.database import get_db
from shop_service.deps import get_current_user
from shop_service.models import Order, OrderItem, Product, User
from shop_service.schemas import OrderCreate

router = APIRouter(
    prefix="/api/orders",
    tags=["订单管理"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_order(
    body: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建订单：校验 → 算金额 → 扣库存 → 写库"""
    # 同一订单里相同商品合并数量，避免重复行
    merged: dict[int, int] = {}
    for item in body.items:
        merged[item.product_id] = merged.get(item.product_id, 0) + item.quantity

    order_items = []
    total_amount = 0.0

    for product_id, quantity in merged.items():
        product = db.get(Product, product_id)
        # 校验 1：商品存在
        if product is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"商品 {product_id} 不存在")
        # 校验 2：商品必须上架
        if product.status != 1:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"商品 {product.name} 已下架")
        # 校验 3：库存充足
        if product.stock < quantity:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"商品 {product.name} 库存不足，剩余 {product.stock}，需要 {quantity}",
            )

        # 用数据库单价算金额，不信前端价格
        total_amount += float(product.price) * quantity
        # 预扣库存
        product.stock -= quantity
        # 订单项（快照：下单时的名称和单价）
        order_items.append(OrderItem(
            product_id=product.id,
            product_name=product.name,
            quantity=quantity,
            price=product.price,
        ))

    # 生成订单号：时间戳 + 随机串，保证业务唯一
    order_no = f"ORD{time.strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}"

    order = Order(
        order_no=order_no,
        user_id=current_user.id,
        total_amount=round(total_amount, 2),
        status=0,  # 待支付
    )
    order.items = order_items

    db.add(order)
    db.commit()
    db.refresh(order)
    return success(_order_to_dict(order), "下单成功")


@router.get("")
def list_orders(
    order_status: int | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """订单列表：只能看自己的订单"""
    stmt = select(Order).where(Order.user_id == current_user.id)
    if order_status is not None:
        stmt = stmt.where(Order.status == order_status)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(
        stmt.order_by(Order.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return success({
        "total": total,
        "page": page,
        "page_size": page_size,
        "list": [_order_to_dict(o) for o in rows],
    })


@router.get("/{order_no}")
def get_order(order_no: str, db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    """订单详情"""
    order = _get_owned_order(db, order_no, current_user)
    return success(_order_to_dict(order))


@router.post("/{order_no}/cancel")
def cancel_order(order_no: str, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    """取消订单：只有待支付能取消，回补库存"""
    order = _get_owned_order(db, order_no, current_user)

    if order.status != 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "只有待支付订单能取消")

    # 回补库存
    for item in order.items:
        product = db.get(Product, item.product_id)
        if product is not None:
            product.stock += item.quantity

    order.status = 2  # 已取消
    db.commit()
    db.refresh(order)
    return success(_order_to_dict(order), "取消成功")


def _get_owned_order(db: Session, order_no: str, current_user: User) -> Order:
    """查订单并校验归属：不能看别人的订单"""
    order = db.scalar(select(Order).where(Order.order_no == order_no))
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "订单不存在")
    if order.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "不能操作别人的订单")
    return order


def _order_to_dict(order: Order) -> dict:
    """订单转响应字典"""
    return {
        "id": order.id,
        "order_no": order.order_no,
        "total_amount": float(order.total_amount),
        "status": order.status,
        "create_time": str(order.create_time),
        "pay_time": str(order.pay_time) if order.pay_time else None,
        "items": [
            {
                "product_id": it.product_id,
                "product_name": it.product_name,
                "quantity": it.quantity,
                "price": float(it.price),
            }
            for it in order.items
        ],
    }
