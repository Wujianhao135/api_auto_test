"""
服务配置：所有可调参数集中在这里，支持环境变量覆盖。
本地开发用默认值，CI/生产环境通过环境变量传入，避免把密码写死在代码里。
"""
import os

# 数据库连接串：mysql+pymysql 驱动，连接本地 shop 库
# 环境变量 DB_URL 优先，没有就用本地开发默认值
DB_URL = os.environ.get(
    "SHOP_DB_URL",
    "mysql+pymysql://root:hsp@localhost:3306/shop?charset=utf8mb4",
)

# JWT 配置
JWT_SECRET = os.environ.get("SHOP_JWT_SECRET", "shop-secret-key-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60  # token 有效期 60 分钟

# 支付回调验签密钥（模拟和支付平台约定的密钥）
PAY_SECRET = os.environ.get("SHOP_PAY_SECRET", "pay-secret-2026")
