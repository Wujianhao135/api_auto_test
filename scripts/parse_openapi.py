"""
接口文档解析脚本（阶段 1 产出）

从若依 OpenAPI 文档（/v3/api-docs）拉取全部接口，解析成 Markdown 接口清单。
这份清单后续作为编写测试用例的 Checklist：每条接口至少覆盖一个正常 + 一个异常用例。

运行方式（在项目根目录）：
  .venv\\Scripts\\python.exe scripts\\parse_openapi.py
  .venv\\Scripts\\python.exe scripts\\parse_openapi.py --base-url http://localhost:8080
  .venv\\Scripts\\python.exe scripts\\parse_openapi.py -o docs/api_inventory.md
"""
import argparse
import os

import requests

# 若依实际公开的接口（未登录即可访问），其余接口都需要 Bearer Token
# 说明：OpenAPI 顶层默认要求鉴权，但这几个接口在 Spring Security 配置里放行了
PUBLIC_PATHS = {
    ("post", "/login"),
    ("get", "/captchaImage"),
    ("post", "/register"),
}

# 模块分组规则：按路径第一段归类，顺序即输出顺序
MODULE_ORDER = [
    ("登录认证", ["/login", "/captchaImage", "/register", "/getInfo",
                 "/getRouters", "/unlockscreen"]),
    ("用户管理", ["/system/user"]),
    ("角色管理", ["/system/role"]),
    ("岗位管理", ["/system/post"]),
    ("部门管理", ["/system/dept"]),
    ("菜单管理", ["/system/menu"]),
    ("字典管理", ["/system/dict"]),
    ("参数配置", ["/system/config"]),
    ("通知公告", ["/system/notice"]),
    ("监控运维", ["/monitor"]),
    ("文件上传下载", ["/common"]),
    ("代码生成", ["/tool"]),
]

HTTP_METHODS = ["get", "post", "put", "delete"]

# operationId 中文映射（若依 controller 没写 @Operation(summary)，用方法名兜底翻译）
# 带数字后缀的 operationId（如 add_1、remove_3）先去掉后缀再查表
OPERATION_CN = {
    "login": "登录", "getCode": "获取验证码", "getInfo": "获取当前用户信息",
    "getRouters": "获取路由菜单", "register": "注册", "unlockScreen": "解锁屏幕",
    "add": "新增", "edit": "修改", "remove": "删除", "list": "列表查询",
    "export": "导出", "importData": "导入数据", "importTemplate": "下载导入模板",
    "resetPwd": "重置密码", "changeStatus": "修改状态", "profile": "个人信息",
    "updateProfile": "修改个人信息", "updatePwd": "修改密码", "avatar": "上传头像",
    "deptTree": "部门树", "optionselect": "下拉选项", "treeselect": "树选择",
    "refreshCache": "刷新缓存", "clean": "清空数据", "run": "执行一次",
    "forceLogout": "强制退出", "markRead": "标记已读", "markReadAll": "全部已读",
    "getConfigKey": "按参数键查询", "authRole": "查询已授权角色",
    "insertAuthRole": "授权角色", "dataScope": "分配数据权限",
    "allocatedList": "已授权用户列表", "unallocatedList": "未授权用户列表",
    "cancelAuthUser": "取消授权", "cancelAuthUserAll": "批量取消授权",
    "selectAuthUserAll": "批量授权", "excludeChild": "排除指定节点的部门列表",
    "updateSort": "修改排序", "roleMenuTreeselect": "按角色查菜单树",
    "dictType": "按类型查字典数据", "readUsersList": "已读用户列表",
    "listTop": "置顶公告列表", "cache": "缓存监控", "getCacheKeys": "查缓存键",
    "getCacheValue": "查缓存值", "clearCacheName": "按名清缓存",
    "clearCacheKey": "按键清缓存", "clearCacheAll": "清空全部缓存",
    "getJobLog": "任务日志", "unlock": "解锁账号", "fileDownload": "文件下载",
    "resourceDownload": "资源下载", "uploadFile": "上传文件", "uploadFiles": "批量上传",
    "genList": "生成表列表", "dataList": "数据库表列表", "columnList": "字段列表",
    "preview": "预览代码", "genCode": "生成代码", "batchGenCode": "批量生成",
    "importTableSave": "导入表", "createTableSave": "新建表", "synchDb": "同步数据库",
    "download": "下载代码", "editSave": "编辑保存",
}


def cn_summary(operation_id: str) -> str:
    """把 operationId 翻译成中文，查不到就原样返回"""
    # 去掉 springdoc 加的数字后缀（add_1 -> add）
    base = operation_id.rsplit("_", 1)[0] if "_" in operation_id else operation_id
    return OPERATION_CN.get(base, operation_id)


def fetch_openapi(base_url: str) -> dict:
    """拉取 OpenAPI JSON 文档"""
    url = base_url.rstrip("/") + "/v3/api-docs"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def extract_endpoint(path: str, method: str, spec: dict) -> dict:
    """
    从单个 path+method 的 OpenAPI 片段提取关键信息：
    方法、路径、说明、鉴权要求、路径参数、是否有请求体
    """
    # 说明：优先用 summary，没有就用 operationId 翻译成中文
    summary = spec.get("summary") or cn_summary(spec.get("operationId", "")) or "(无说明)"

    # 鉴权：命中公开列表则为"公开"，否则需要 Token
    auth = "公开" if (method.lower(), path) in PUBLIC_PATHS else "需Token"

    # 路径参数：从路径里的 {xxx} 提取
    path_params = [p.strip("{}") for p in path.split("/") if p.startswith("{")]

    # 请求体：看 requestBody 里有没有 application/json
    has_body = "requestBody" in spec

    return {
        "method": method.upper(),
        "path": path,
        "summary": summary,
        "auth": auth,
        "path_params": ", ".join(path_params) if path_params else "-",
        "has_body": "JSON" if has_body else "-",
    }


def collect_endpoints(api: dict) -> list:
    """遍历 paths，收集所有接口"""
    endpoints = []
    for path, methods in api.get("paths", {}).items():
        for method, spec in methods.items():
            if method.lower() in HTTP_METHODS:
                endpoints.append(extract_endpoint(path, method, spec))
    return endpoints


def which_module(path: str) -> str:
    """根据路径判断属于哪个模块"""
    for module_name, prefixes in MODULE_ORDER:
        for prefix in prefixes:
            if path == prefix or path.startswith(prefix + "/"):
                return module_name
    return "其他"


def render_markdown(endpoints: list, base_url: str) -> str:
    """把接口列表渲染成 Markdown"""
    lines = []
    lines.append("# 若依接口清单（自动生成）")
    lines.append("")
    lines.append(f"> 数据源：{base_url.rstrip('/')}/v3/api-docs")
    lines.append(f"> 生成时间：脚本运行时，请勿手工编辑；接口变更后重新跑 `parse_openapi.py`")
    lines.append(f"> 接口总数：**{len(endpoints)}**")
    lines.append("")

    # 按模块分组
    modules = {}
    for ep in endpoints:
        modules.setdefault(which_module(ep["path"]), []).append(ep)

    # 按 MODULE_ORDER 的顺序输出，"其他"放最后
    ordered_names = [m[0] for m in MODULE_ORDER] + ["其他"]
    for name in ordered_names:
        if name not in modules:
            continue
        eps = modules[name]
        lines.append(f"## {name}（{len(eps)} 个）")
        lines.append("")
        lines.append("| 方法 | 路径 | 说明 | 鉴权 | 路径参数 | Body |")
        lines.append("|---|---|---|---|---|---|")
        for ep in sorted(eps, key=lambda x: (x["path"], x["method"])):
            lines.append(
                f"| {ep['method']} | `{ep['path']}` | {ep['summary']} | "
                f"{ep['auth']} | {ep['path_params']} | {ep['has_body']} |"
            )
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="解析若依 OpenAPI 文档，生成接口清单")
    parser.add_argument("--base-url", default="http://localhost:8080",
                        help="若依后端地址，默认 http://localhost:8080")
    parser.add_argument("-o", "--output", default=None,
                        help="输出 Markdown 路径，默认 docs/api_inventory.md")
    args = parser.parse_args()

    # 拉取并解析
    api = fetch_openapi(args.base_url)
    endpoints = collect_endpoints(api)

    # 输出路径：默认放到项目 docs/ 下
    if args.output:
        out_path = args.output
    else:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        out_path = os.path.join(project_root, "docs", "api_inventory.md")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    content = render_markdown(endpoints, args.base_url)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"接口清单已生成：{out_path}")
    print(f"共 {len(endpoints)} 个接口")


if __name__ == "__main__":
    main()
