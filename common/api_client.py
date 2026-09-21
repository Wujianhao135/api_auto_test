import logging

import requests
import yaml


class ApiClient:
    """接口请求客户端：统一处理 base_url、headers、超时、异常、日志"""

    def __init__(self, config_path="config/config.yaml"):
        """
        初始化客户端：从配置文件读取 base_url 和超时时间
        """
        # 读取配置文件
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        self.base_url = config.get("base_url", "").rstrip("/")
        self.timeout = config.get("timeout", 10)

        # 创建 Session，自动保持会话（Cookie）
        self.session = requests.Session()

        # 设置默认请求头
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

        # 初始化日志
        self.logger = logging.getLogger(__name__)

    def set_token(self, token):
        """登录成功后调用，把 token 加到请求头里"""
        self.session.headers["Authorization"] = f"Bearer {token}"

    def get(self, path, params=None, headers=None):
        """
        发 GET 请求
        :param path: 接口路径，如 /users
        :param params: URL 参数，如 {"page": 1}
        :param headers: 额外请求头
        :return: 响应对象，失败返回 None
        """
        url = self.base_url + path
        self.logger.info(f"GET 请求: {url}")

        try:
            resp = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            self.logger.info(f"GET 响应状态码: {resp.status_code}")
            return resp
        except requests.exceptions.Timeout:
            self.logger.error(f"请求超时: {url}")
            return None
        except requests.exceptions.ConnectionError:
            self.logger.error(f"连接失败: {url}")
            return None
        except Exception as e:
            self.logger.error(f"请求异常: {e}")
            return None

    def post(self, path, json=None, headers=None):
        """
        发 POST 请求（JSON body）
        :param path: 接口路径，如 /login
        :param json: 请求体字典
        :param headers: 额外请求头
        :return: 响应对象，失败返回 None
        """
        url = self.base_url + path
        self.logger.info(f"POST 请求: {url}")
        self.logger.info(f"POST 请求体: {json}")

        try:
            resp = self.session.post(
                url,
                json=json,
                headers=headers,
                timeout=self.timeout
            )
            self.logger.info(f"POST 响应状态码: {resp.status_code}")
            return resp
        except requests.exceptions.Timeout:
            self.logger.error(f"请求超时: {url}")
            return None
        except requests.exceptions.ConnectionError:
            self.logger.error(f"连接失败: {url}")
            return None
        except Exception as e:
            self.logger.error(f"请求异常: {e}")
            return None

    def delete(self, path, headers=None):
        """发 DELETE 请求"""
        url = self.base_url + path
        self.logger.info(f"DELETE 请求: {url}")

        try:
            resp = self.session.delete(
                url,
                headers=headers,
                timeout=self.timeout
            )
            self.logger.info(f"DELETE 响应状态码: {resp.status_code}")
            return resp
        except Exception as e:
            self.logger.error(f"请求异常: {e}")
            return None
