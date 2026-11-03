"""阶段 3 骨架验证：确认各 fixture 能正常注入和访问接口（阶段 6 会替换为正式用例）"""
import pytest


@pytest.mark.smoke
def test_config_loaded(config):
    """配置能加载"""
    assert config.env in ("dev", "ci")
    assert config.ruoyi.base_url
    assert config.shop.base_url


@pytest.mark.smoke
def test_ruoyi_public_api(ruoyi_client):
    """未登录客户端能访问若依公开接口"""
    resp = ruoyi_client.get("/captchaImage")
    assert resp.status_code == 200


@pytest.mark.smoke
def test_ruoyi_logged(ruoyi_logged):
    """已登录若依客户端能访问受保护接口"""
    resp = ruoyi_logged.get("/getInfo")
    assert resp.status_code == 200
    assert resp.json()["user"]["userName"] == "admin"


@pytest.mark.smoke
def test_shop_logged(shop_logged):
    """已登录电商客户端能访问受保护接口"""
    resp = shop_logged.get("/api/products")
    assert resp.status_code == 200
    assert "list" in resp.json()["data"]
