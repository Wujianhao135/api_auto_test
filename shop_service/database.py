"""
数据库连接：创建 engine、Session 工厂和模型基类。
所有 ORM 模型都继承这里的 Base，所有路由通过 get_db 拿会话。
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from shop_service.config import DB_URL

# engine：管理数据库连接池
engine = create_engine(DB_URL, pool_pre_ping=True, pool_recycle=3600)

# SessionLocal：每个请求创建一个独立会话
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """所有 ORM 模型的基类"""
    pass


def get_db():
    """
    FastAPI 依赖：请求开始建会话，请求结束自动关闭。
    用法：路由参数写 db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
