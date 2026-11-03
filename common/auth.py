"""
鉴权封装：两个系统的登录流程。
  - login_ruoyi：若依登录（获取验证码 → Redis 读答案 → 登录拿 token）
  - login_shop：电商服务登录（JWT）

两个函数都返回 token 字符串，供 ApiClient.set_token 使用。
"""
from common.api_client import ApiClient
from common.logger import get_logger
from common.redis_util import RedisUtil

logger = get_logger("auth")


def login_ruoyi(client: ApiClient, username: str, password: str) -> str:
    """
    若依登录完整流程：
      1. 调 captchaImage 获取 uuid；
      2. 从 Redis 读验证码答案；
      3. 带账号、密码、验证码、uuid 调 /login；
      4. 校验业务码，返回 token。
    """
    # 1. 获取验证码
    resp = client.get("/captchaImage")
    captcha = resp.json()

    # 兼容验证码被关闭的情况：captchaEnabled=false 时没有 uuid
    if not captcha.get("captchaEnabled"):
        logger.info("若依验证码已关闭，直接登录")
        login_resp = client.post("/login", json={"username": username, "password": password})
    else:
        uuid = captcha["uuid"]
        # 2. 从 Redis 读答案
        redis_util = RedisUtil()
        code = redis_util.get_captcha_answer(uuid)
        logger.info(f"从 Redis 读到验证码答案: {code}")
        # 3. 带验证码登录
        login_resp = client.post("/login", json={
            "username": username,
            "password": password,
            "code": code,
            "uuid": uuid,
        })

    # 4. 校验业务码（若依登录失败 HTTP 也是 200，靠 code 判断）
    data = login_resp.json()
    if data.get("code") != 200:
        raise RuntimeError(f"若依登录失败: {data.get('msg')}")
    return data["token"]


def login_shop(client: ApiClient, username: str, password: str) -> str:
    """电商 JWT 登录：POST /api/auth/login，返回 access_token"""
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    data = resp.json()
    # 电商登录失败返回 401/400，成功结构为 data.access_token
    if data.get("code") != 200:
        raise RuntimeError(f"电商登录失败: {data.get('msg') or data.get('detail')}")
    return data["data"]["access_token"]
