import os
import sys
import yaml
import pytest
from common.assertions import assert_response

# 把项目根目录加入路径，让 tests 能 import common
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.api_client import ApiClient

# 读取 YAML 测试数据
data_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "login_data.yaml"
)
with open(data_path, encoding="utf-8") as f:
    login_data = yaml.safe_load(f)["login"]

@pytest.mark.parametrize("case", login_data, ids=lambda x: x["title"])
def test_login(case):
    """
    登录测试：从 YAML 读取数据驱动
    :param case: YAML 里的每一条数据
    """
    client = ApiClient("config/config.yaml")
    resp = client.post("/login", json=case["payload"])

    assert_response(resp, case["expected_code"])

    result = resp.json()
    assert case["expected_field"] in result