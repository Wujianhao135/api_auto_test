# 接口自动化测试框架

基于 Python + requests + pytest 的接口自动化测试项目。

## 技术栈

- Python 3.10
- requests（发请求）
- pytest（测试框架）
- pytest-html（测试报告）
- pyyaml（配置文件）

## 项目结构

api_auto_test/
├── config/
│   └── config.yaml          # 环境配置
├── data/
│   └── test_data.json       # 测试数据
├── common/
│   ├── api_client.py        # requests 封装
│   └── logger.py            # 日志封装
├── tests/
│   ├── conftest.py          # 公共 fixture
│   ├── test_login.py         # 登录用例
│   └── test_user_crud.py     # 用户增删改查
├── reports/                 # 测试报告
├── requirements.txt
└── pytest.ini

```
## 快速开始

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 运行所有测试

```
pytest
```

3. 生成 HTML 报告

```
pytest --html=reports/report.html
```

4. 只跑冒烟测试

```
pytest -m smoke
```

## 测试覆盖

- 登录：正常登录、空邮箱、空密码、缺少密码
- 用户管理：创建用户、查列表、查详情、删除用户