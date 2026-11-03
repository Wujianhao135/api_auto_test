"""
电商服务初始化数据：插入测试用户。
可重复执行：用户已存在就跳过，不会重复插入。

运行方式（在项目根目录）：
  .venv\\Scripts\\python.exe scripts/init_shop_data.py
"""
import os
import sys

from sqlalchemy import select

# 把项目根目录加入路径，让脚本能 import shop_service
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shop_service.database import SessionLocal
from shop_service.models import User
from shop_service.security import hash_password

# 初始化的测试账号
SEED_USERS = [
    {"username": "admin", "password": "admin123", "nickname": "管理员"},
    {"username": "testuser", "password": "test123", "nickname": "测试用户"},
]


def main():
    db = SessionLocal()
    try:
        for seed in SEED_USERS:
            exists = db.scalar(select(User).where(User.username == seed["username"]))
            if exists:
                print(f"用户 {seed['username']} 已存在，跳过")
                continue
            user = User(
                username=seed["username"],
                password=hash_password(seed["password"]),
                nickname=seed["nickname"],
                status=1,
            )
            db.add(user)
            print(f"已创建用户 {seed['username']} / {seed['password']}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
