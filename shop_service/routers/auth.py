"""
认证路由：登录接口（公开，不需要 token）。
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from shop_service.common import success
from shop_service.database import get_db
from shop_service.models import User
from shop_service.schemas import LoginRequest
from shop_service.security import create_access_token, verify_password

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """登录：校验账号密码，返回 JWT"""
    # 1. 按用户名查用户
    user = db.scalar(select(User).where(User.username == body.username))

    # 2. 用户不存在或密码错误，统一返回 401（不暴露具体是哪个错了）
    if user is None or not verify_password(body.password, user.password):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "用户名或密码错误"
        )

    # 3. 账号停用
    if user.status != 1:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "账号已停用")

    # 4. 生成 token 返回
    token = create_access_token(user.id)
    return success({"access_token": token, "token_type": "bearer"}, "登录成功")
