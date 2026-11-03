"""
商品路由：增删改查、上下架，全部需要登录。
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError as SAIntegrityError
from sqlalchemy.orm import Session

from shop_service.common import success
from shop_service.database import get_db
from shop_service.deps import get_current_user
from shop_service.models import Product, User
from shop_service.schemas import ProductCreate, ProductStatus, ProductUpdate

router = APIRouter(
    prefix="/api/products",
    tags=["商品管理"],
    dependencies=[Depends(get_current_user)],  # 整个路由都要登录
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_product(
    body: ProductCreate,
    db: Session = Depends(get_db),
):
    """新增商品：名称不能重复"""
    product = Product(
        name=body.name,
        price=body.price,
        stock=body.stock,
        status=1,  # 新增默认上架
        description=body.description,
    )
    db.add(product)
    try:
        db.commit()
    except SAIntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"商品名 {body.name} 已存在")
    db.refresh(product)
    return success(_to_dict(product), "新增成功")


@router.get("")
def list_products(
    name: str | None = Query(None, description="按名称模糊搜索"),
    product_status: int | None = Query(None, alias="status", description="按状态筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """商品列表：分页 + 名称搜索 + 状态筛选"""
    stmt = select(Product)
    if name:
        stmt = stmt.where(Product.name.like(f"%{name}%"))
    if product_status is not None:
        stmt = stmt.where(Product.status == product_status)

    # 先查总数（用子查询统计，保证和筛选条件一致）
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    # 分页
    rows = db.scalars(
        stmt.order_by(Product.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return success({
        "total": total,
        "page": page,
        "page_size": page_size,
        "list": [_to_dict(p) for p in rows],
    })


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """查单个商品详情"""
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "商品不存在")
    return success(_to_dict(product))


@router.put("/{product_id}")
def update_product(
    product_id: int,
    body: ProductUpdate,
    db: Session = Depends(get_db),
):
    """修改商品：只更新传了的字段"""
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "商品不存在")

    # exclude_unset：只拿请求里实际传了的字段
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    try:
        db.commit()
    except SAIntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "商品名已存在")
    db.refresh(product)
    return success(_to_dict(product), "修改成功")


@router.put("/{product_id}/status")
def change_status(
    product_id: int,
    body: ProductStatus,
    db: Session = Depends(get_db),
):
    """商品上下架"""
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "商品不存在")
    product.status = body.status
    db.commit()
    return success(_to_dict(product), "状态更新成功")


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """删除商品"""
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "商品不存在")
    db.delete(product)
    db.commit()


def _to_dict(product: Product) -> dict:
    """把商品对象转成响应字典（Decimal 转 float 方便 JSON 序列化）"""
    return {
        "id": product.id,
        "name": product.name,
        "price": float(product.price),
        "stock": product.stock,
        "status": product.status,
        "description": product.description,
        "create_time": str(product.create_time),
    }
