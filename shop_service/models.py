"""
ORM 模型：每个类对应 shop 库里的一张表。
字段类型和约束与 sql/shop.sql 保持一致。
"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shop_service.database import Base


class User(Base):
    """用户表：登录账号"""
    __tablename__ = "shop_user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    nickname: Mapped[str] = mapped_column(String(50), nullable=True)
    status: Mapped[int] = mapped_column(TINYINT, default=1)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Product(Base):
    """商品表"""
    __tablename__ = "shop_product"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    stock: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(TINYINT, default=1)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class Order(Base):
    """订单表：status 0待支付 1已支付 2已取消"""
    __tablename__ = "shop_order"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(32), unique=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2))
    status: Mapped[int] = mapped_column(TINYINT, default=0)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    pay_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # 关联订单项：order.items 直接拿到该订单所有订单项
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    """订单项表：下单时的商品快照"""
    __tablename__ = "shop_order_item"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("shop_order.id"), index=True
    )
    product_id: Mapped[int] = mapped_column(BigInteger)
    product_name: Mapped[str] = mapped_column(String(100))
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Numeric(10, 2))

    order: Mapped["Order"] = relationship(back_populates="items")


class PaymentRecord(Base):
    """支付记录表：每次回调留一条"""
    __tablename__ = "shop_payment_record"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(32), index=True)
    pay_amount: Mapped[float] = mapped_column(Numeric(10, 2))
    pay_status: Mapped[int] = mapped_column(TINYINT)
    transaction_id: Mapped[str] = mapped_column(String(64), nullable=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
