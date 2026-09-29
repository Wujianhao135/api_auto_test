# common/assertions.py

def assert_response(resp, expected_code, expected_fields=None):
    """
    统一断言方法
    :param resp: requests 返回的响应对象
    :param expected_code: 预期状态码，比如 200、201、404
    :param expected_fields: 预期响应体里必须有的字段，比如 ["id", "name"]
    """
    # 1. 断言响应不为空（请求不能失败）
    assert resp is not None, "请求失败，返回了 None"

    # 2. 断言状态码
    assert resp.status_code == expected_code, \
        f"状态码不对：预期 {expected_code}，实际 {resp.status_code}"

    # 3. 如果指定了要检查的字段，就检查响应体里有没有
    if expected_fields:
        resp_json = resp.json()
        for field in expected_fields:
            assert field in resp_json, \
                f"响应体里没有字段 {field}，实际返回：{resp_json}"
