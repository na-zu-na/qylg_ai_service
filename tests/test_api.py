from fastapi.testclient import TestClient

from core.exception import AIResultParseError
from main import app


client = TestClient(app)


def test_health_endpoint_returns_service_metadata():
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["message"] == "ok"
    assert payload["data"]["service"]
    assert payload["data"]["env"]


def test_parse_product_query_success(monkeypatch):
    def fake_parse_product_query(text: str):
        assert text == "送女生的中式摆件"
        return {
            "type": "mass",
            "keyword": "中式摆件",
            "title": None,
            "purpose": "送礼",
            "price_min": None,
            "price_max": 300,
            "size_range": "小型摆件",
            "make_time": None,
            "sort_by": "recommend",
            "status": 1,
        }

    monkeypatch.setattr(
        "api.routes_product_parse.parser_service.parse_product_query",
        fake_parse_product_query,
    )

    response = client.post(
        "/api/parse/product-query",
        json={"text": "送女生的中式摆件"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 200,
        "message": "success",
        "data": {
            "type": "mass",
            "keyword": "中式摆件",
            "title": None,
            "purpose": "送礼",
            "price_min": None,
            "price_max": 300.0,
            "size_range": "小型摆件",
            "make_time": None,
            "sort_by": "recommend",
            "status": 1,
        },
    }


def test_parse_product_query_validation_error():
    response = client.post("/api/parse/product-query", json={"text": ""})

    assert response.status_code == 422
    payload = response.json()
    assert payload["code"] == 422
    assert payload["data"]


def test_parse_product_query_internal_error(monkeypatch):
    def fake_parse_product_query(_: str):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "api.routes_product_parse.parser_service.parse_product_query",
        fake_parse_product_query,
    )

    response = client.post(
        "/api/parse/product-query",
        json={"text": "帮我找礼物"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "商品查询解析失败: boom"


def test_custom_product_success(monkeypatch):
    def fake_parse_custom_product(req):
        assert req.text == "做一个中式礼物"
        return {
            "purpose": "送礼",
            "style": "中式",
            "material": "木质",
            "budgetRange": "100-300",
            "size": None,
            "remark": "带包装",
            "colors": ["红色", "金色"],
            "patterns": ["祥云"],
            "aiRemark": "适合节日送礼",
        }

    monkeypatch.setattr(
        "api.routes_ai_custom_product.ai_custom_product_service.parse_custom_product",
        fake_parse_custom_product,
    )

    response = client.post(
        "/api/ai/custom-product",
        json={
            "text": "做一个中式礼物",
            "purposeList": ["送礼", "自用"],
            "styleList": ["中式", "现代"],
            "materialList": ["木质", "陶瓷"],
            "budgetRangeList": ["100以内", "100-300"],
            "colorList": ["红色", "金色"],
            "patternList": ["祥云", "山水"],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "code": 200,
        "message": "success",
        "data": {
            "purpose": "送礼",
            "style": "中式",
            "material": "木质",
            "budgetRange": "100-300",
            "size": None,
            "remark": "带包装",
            "colors": ["红色", "金色"],
            "patterns": ["祥云"],
            "aiRemark": "适合节日送礼",
        },
    }


def test_custom_product_app_exception(monkeypatch):
    def fake_parse_custom_product(_):
        raise AIResultParseError("结果解析失败")

    monkeypatch.setattr(
        "api.routes_ai_custom_product.ai_custom_product_service.parse_custom_product",
        fake_parse_custom_product,
    )

    response = client.post(
        "/api/ai/custom-product",
        json={
            "text": "做一个中式礼物",
            "purposeList": ["送礼"],
            "styleList": ["中式"],
            "materialList": ["木质"],
            "budgetRangeList": ["100-300"],
            "colorList": ["红色"],
            "patternList": ["祥云"],
        },
    )

    assert response.status_code == 500
    assert response.json() == {
        "code": 5002,
        "msg": "结果解析失败",
        "data": None,
    }
