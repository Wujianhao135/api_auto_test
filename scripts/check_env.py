"""
环境连通性检查脚本（阶段 0 产出）

检查项：
  1. MySQL 端口 3306 是否可达
  2. Redis 端口 6379 是否可达
  3. 若依后端端口 8080 是否可达
  4. 若依验证码接口 /captchaImage 是否正常（公开接口，无需登录）
  5. 若依 OpenAPI 文档 /v3/api-docs 是否可访问

运行方式（在项目根目录）：
  .venv\\Scripts\\python.exe scripts\\check_env.py
"""
import socket

import requests

# 统一管理要检查的目标，方便后续维护
PORT_TARGETS = [
    ("MySQL 数据库", "localhost", 3306),
    ("Redis 缓存", "localhost", 6379),
    ("若依后端", "localhost", 8080),
]

HTTP_TARGETS = [
    ("若依验证码接口", "http://localhost:8080/captchaImage"),
    ("若依 OpenAPI 文档", "http://localhost:8080/v3/api-docs"),
]


def check_port(name, host, port, timeout=3):
    """用 socket 探测端口是否可连接"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, f"{name} {host}:{port} 可连接"
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        return False, f"{name} {host}:{port} 连不上：{e}"


def check_http(name, url, timeout=5):
    """用 requests 探测 HTTP 接口是否返回 200"""
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            return True, f"{name} 正常（HTTP 200）"
        return False, f"{name} 状态码异常：{resp.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"{name} 请求失败：{e}"


def main():
    """执行全部检查并汇总结果"""
    results = []

    print("=" * 60)
    print("接口自动化项目 - 环境连通性检查")
    print("=" * 60)

    # 1. 端口类检查
    for name, host, port in PORT_TARGETS:
        ok, msg = check_port(name, host, port)
        results.append(ok)
        print(f"[{'PASS' if ok else 'FAIL'}] {msg}")

    # 2. HTTP 类检查
    for name, url in HTTP_TARGETS:
        ok, msg = check_http(name, url)
        results.append(ok)
        print(f"[{'PASS' if ok else 'FAIL'}] {msg}")

    # 3. 汇总
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"检查结果：{passed}/{total} 通过")

    if all(results):
        print("环境就绪，可以进入下一阶段。")
        return 0
    print("存在未通过项，请先启动对应服务（若依双击 启动若依.bat）。")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
