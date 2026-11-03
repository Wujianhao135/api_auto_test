# 接口自动化测试项目

基于 Python + pytest 的接口自动化测试框架，覆盖**若依后台管理系统**和**FastAPI 半真实电商服务**，包含登录、用户、商品、订单、支付回调全流程，支持三层断言、Allure 报告、GitHub Actions 定时执行。

## 项目架构

```
┌─────────────────────────────────────────────────────┐
│  测试框架（pytest + requests）                       │
│  ├─ common/   请求封装、鉴权、数据工厂、三层断言、日志 │
│  ├─ tests/    50 个测试用例（正常:异常 ≈ 6:4）       │
│  └─ reports/  Allure / HTML 报告、日志               │
└──────────────┬──────────────────────┬───────────────┘
               │                      │
       ┌───────▼────────┐     ┌───────▼────────┐
       │ 若依 RuoYi     │     │ FastAPI 电商    │
       │ Spring Boot    │     │ 商品/订单/支付  │
       │ 8080 端口      │     │ 8000 端口       │
       └───────┬────────┘     └───────┬────────┘
               │                      │
       ┌───────▼──────────────────────▼───────┐
       │  MySQL（ry-vue 库 + shop 库）+ Redis  │
       └──────────────────────────────────────┘
```

## 环境要求

| 组件 | 版本 | 说明 |
|---|---|---|
| Python | 3.11+ | 测试框架和电商服务 |
| MySQL | 8.0+ | 存业务数据 |
| Redis | 5.0+ | 若依验证码、登录缓存 |
| JDK | 17 | 若依后端运行（仅跑若依用例时需要） |
| Allure CLI | 2.46+ | 生成 Allure 报告（可选，用 npm 装） |

## 快速开始

### 1. 克隆并安装依赖

```bash
git clone <你的仓库地址>
cd api_auto_test
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 初始化数据库

确保 MySQL 已启动，然后执行建表脚本：

```bash
mysql -u root -p < sql/shop.sql
```

若依数据库请按若依官方文档初始化 `ry-vue` 库。

### 3. 配置环境

编辑 `config/config.yaml`，确认数据库账号密码、服务地址。敏感信息建议用环境变量覆盖：

```powershell
# Windows PowerShell
$env:MYSQL_PASSWORD = "你的密码"
$env:SHOP_PAY_SECRET = "支付密钥"
```

### 4. 启动被测服务

**电商服务（必须）：**
```bash
python -m uvicorn shop_service.main:app --host 127.0.0.1 --port 8000
```

**若依后端（跑若依用例时需要）：**
```bash
java -jar ruoyi-admin/target/ruoyi-admin.jar
```

### 5. 跑测试

```bash
# 全部 50 个用例（需要两个服务都启动）
pytest tests/

# 只跑电商用例（跳过若依）
pytest tests/ -m "not ruoyi"

# 只跑冒烟
pytest tests/ -m smoke
```

### 6. 看报告

```bash
# 一键生成 Allure 报告（Windows）
powershell -File scripts/run_with_allure.ps1

# 或手动两步
pytest tests/ --alluredir reports/allure-results
allure generate reports/allure-results -o reports/allure-report --clean
# 打开 reports/allure-report/index.html
```

pytest-html 快速报告在 `reports/report.html`。

## 目录结构

```
api_auto_test/
├── common/                  # 核心封装
│   ├── api_client.py        # HTTP 请求客户端，统一记录请求/响应
│   ├── assertions.py        # 三层断言（HTTP/业务码/数据库）
│   ├── auth.py              # 若依/电商登录封装
│   ├── config_loader.py     # 多环境配置加载
│   ├── data_factory.py      # 数据工厂，造测试数据
│   ├── db_util.py           # MySQL 工具，数据清理
│   ├── logger.py            # 日志（控制台+文件）
│   └── redis_util.py        # Redis 工具，读验证码
├── config/
│   └── config.yaml          # dev/ci 双环境配置
├── shop_service/            # FastAPI 半真实电商服务
│   ├── routers/             # 商品/订单/支付/认证路由
│   ├── models.py            # SQLAlchemy 模型
│   └── schemas.py           # Pydantic 模型
├── tests/
│   ├── conftest.py          # 全局 fixture
│   ├── test_shop_product.py # 商品用例
│   ├── test_shop_order.py   # 订单用例
│   ├── test_shop_payment.py # 支付用例
│   ├── test_shop_auth.py    # 电商登录用例
│   ├── test_ruoyi_auth.py   # 若依登录用例
│   └── test_ruoyi_user.py   # 若依用户用例
├── scripts/
│   ├── check_env.py         # 环境检查
│   └── run_with_allure.ps1  # 一键 Allure 报告
├── sql/
│   └── shop.sql             # 电商建表脚本
└── .github/workflows/
    └── test.yml             # GitHub Actions CI
```

## 三层断言

每个用例都做三层校验，不只是看 HTTP 200：

```python
# 第一层：HTTP 状态码
assert_http(resp, 201)
# 第二层：业务码 + 响应字段
assert_biz_ok(resp)
assert_data(resp, {"price": 99.5})
# 第三层：数据库真的落库了
assert_db_row(db, "shop_product", {"id": pid}, {"stock": 100})
```

## CI 定时执行

GitHub Actions 每天 UTC 0:00（北京时间 8:00）自动跑，配置见 `.github/workflows/test.yml`：
- CI 里只跑电商用例（38 个），若依用例本地跑；
- Allure 报告自动上传为 artifact，保留 14 天；
- 支持手动触发（workflow_dispatch）。

## 测试数据约定

- 所有测试数据统一带 `auto_test_` 前缀；
- 每个测试 session 开始前自动清理上次残留（conftest autouse fixture）；
- 若依测试用户在 `sys_user` 表，电商数据在 `shop` 库，分开清理。

## 常用命令

```bash
# 环境检查
python scripts/check_env.py

# 单个用例文件
pytest tests/test_shop_product.py -v

# 生成 Allure 报告
pytest tests/ --alluredir reports/allure-results
allure generate reports/allure-results -o reports/allure-report --clean
```
