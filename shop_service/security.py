"""
安全工具：密码哈希、JWT 生成与解析。
密码绝不存明文，用 bcrypt 单向哈希；JWT 里放用户 ID，服务端校验签名。
"""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from shop_service.config import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET


def hash_password(raw: str) -> str:
    """把明文密码哈希后存储（bcrypt 自带盐值）"""
    # bcrypt 要求输入字节，且密码不超过 72 字节
    return bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(raw: str, hashed: str) -> bool:
    """校验明文密码和哈希值是否匹配"""
    return bcrypt.checkpw(raw.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: int) -> str:
    """生成 JWT：载荷里放用户 ID 和过期时间"""
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> int:
    """解析 JWT，返回用户 ID；token 非法或过期会抛异常"""
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return int(payload["sub"])
