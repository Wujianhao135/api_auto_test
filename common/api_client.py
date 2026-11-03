"""
接口请求客户端（重构版）：
  - 支持 GET / POST / PUT / PATCH / DELETE 全部常用方法；
  - 统一 _request 入口，自动记录完整请求与响应、耗时；
  - requests.Session 复用连接，set_token 统一带鉴权头；
  - 网络层异常（超时/连接失败）记录日志后抛出，不返回 None 掩盖问题；
  - 不主动 raise_for_status，保留 4xx/5xx 响应给异常用例断言。

用法：
  client = ApiClient(base_url="http://localhost:8080")
  client.set_token(token)
  resp = client.get("/system/user/list")
"""
import time

import requests

from common.logger import get_logger

# 响应体日志最大长度，防止超长 body 刷屏
_MAX_BODY_LOG = 2000


class ApiClient:
    """接口请求客户端：统一 base_url、鉴权、超时、日志、异常"""

    def __init__(self, base_url: str, timeout: int = 10):
        """
        初始化客户端
        :param base_url: 被测系统根地址，如 http://localhost:8080
        :param timeout: 请求超时秒数
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # Session 复用连接、保持会话
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

        self.logger = get_logger("api_client")

    def set_token(self, token: str):
        """登录成功后调用，把 token 加到默认请求头"""
        self.session.headers["Authorization"] = f"Bearer {token}"

    def clear_token(self):
        """清除鉴权头（用于测试无 token 场景）"""
        self.session.headers.pop("Authorization", None)

    # ===== 各 HTTP 方法，统一走 _request =====
    def get(self, path, params=None, headers=None):
        return self._request("GET", path, params=params, headers=headers)

    def post(self, path, json=None, headers=None):
        return self._request("POST", path, json=json, headers=headers)

    def put(self, path, json=None, headers=None):
        return self._request("PUT", path, json=json, headers=headers)

    def patch(self, path, json=None, headers=None):
        return self._request("PATCH", path, json=json, headers=headers)

    def delete(self, path, json=None, params=None, headers=None):
        return self._request("DELETE", path, json=json, params=params, headers=headers)

    def _request(self, method, path, json=None, params=None, headers=None):
        """统一请求处理：记录请求 → 发送 → 记录响应/异常"""
        url = self.base_url + path
        start = time.time()

        # 记录请求信息（请求头脱敏，不打印完整 token）
        self.logger.info(f"====> {method} {url}")
        if params:
            self.logger.info(f"请求参数 params: {params}")
        if json is not None:
            self.logger.info(f"请求体 json: {json}")
        self.logger.info(f"请求头: {self._mask_headers(headers)}")

        # Allure 附件：把请求信息挂到用例上
        self._attach_allure("请求", f"{method} {url}\n请求体: {json}\n参数: {params}")

        try:
            resp = self.session.request(
                method=method,
                url=url,
                json=json,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout:
            self.logger.error(f"请求超时（{self.timeout}s）: {method} {url}")
            raise
        except requests.exceptions.ConnectionError:
            self.logger.error(f"连接失败（服务是否启动？）: {method} {url}")
            raise
        except requests.exceptions.RequestException:
            self.logger.error(f"请求异常: {method} {url}")
            raise

        cost = time.time() - start
        # 记录响应：状态码、耗时、响应体
        self.logger.info(f"<==== {method} {url} 状态码={resp.status_code} 耗时={cost:.3f}s")
        self.logger.info(f"响应体: {self._cut(resp.text)}")
        # Allure 附件：响应
        self._attach_allure(
            "响应",
            f"状态码: {resp.status_code}  耗时: {cost:.3f}s\n{self._cut(resp.text)}",
        )
        return resp

    @staticmethod
    def _attach_allure(name: str, body: str):
        """把请求/响应挂到 Allure 报告上；非 Allure 模式静默跳过"""
        try:
            import allure
            allure.attach(body, name=name, attachment_type=allure.attachment_type.TEXT)
        except Exception:
            pass  # 非 Allure 运行环境，忽略

    def _mask_headers(self, extra=None) -> dict:
        """合并默认请求头并对 Authorization 脱敏，避免 token 完整落日志"""
        merged = dict(self.session.headers)
        if extra:
            merged.update(extra)
        if "Authorization" in merged:
            token = merged["Authorization"]
            # 只保留前 12 位和长度，中间隐藏
            merged["Authorization"] = f"{token[:12]}...(已脱敏, 长度{len(token)})"
        return merged

    @staticmethod
    def _cut(text: str) -> str:
        """响应体过长时截断"""
        if len(text) > _MAX_BODY_LOG:
            return text[:_MAX_BODY_LOG] + f"...(已截断, 总长{len(text)})"
        return text
