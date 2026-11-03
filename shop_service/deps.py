"""
依赖注入：从请求头解析当前登录用户。
需要登录的路由把参数写成 current_user: User = Depends(get_current_user)。
"""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from shop_service.database import get_db
from shop_service.models import User
from shop_service.security import decode_token

# 自动从 Authorization: Bearer xxx 取 token
bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    """解析 token → 查用户 → 校验用户状态"""
    token = credentials.credentials
    try:
        user_id = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "token 已过期")
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "token 无效")

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "用户不存在")
    if user.status != 1:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "账号已停用")
    return user
