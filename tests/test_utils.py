from schemas.ai_custom_product import AiCustomProductRequest
from utils.custom_product_util import normalize_ai_result
from utils.parser_util import extract_json_from_text, normalize_product_query


def build_custom_request() -> AiCustomProductRequest:
    return AiCustomProductRequest(
        text="想做一个中式送礼摆件",
        purposeList=["送礼", "自用"],
        styleList=["中式", "现代"],
        materialList=["木质", "陶瓷"],
        budgetRangeList=["100以内", "100-300"],
        colorList=["红色", "金色", "黑色"],
        patternList=["祥云", "山水", "花鸟"],
    )


def test_extract_json_from_markdown_block():
    text = """
```json
{"type":"mass","keyword":"摆件"}
```
""".strip()

    result = extract_json_from_text(text)

    assert result == {"type": "mass", "keyword": "摆件"}


def test_extract_json_from_wrapped_text():
    text = '模型输出如下：{"type":"custom","price_max":300} 请查收'

    result = extract_json_from_text(text)

    assert result == {"type": "custom", "price_max": 300}


def test_normalize_product_query_converts_types_and_defaults():
    raw_data = {
        "type": "mass",
        "keyword": "  中式摆件  ",
        "price_min": "100",
        "price_max": "300.5",
        "make_time": "7",
        "sort_by": "",
        "status": 0,
    }

    result = normalize_product_query(raw_data)

    assert result == {
        "type": "mass",
        "keyword": "  中式摆件  ",
        "title": None,
        "purpose": None,
        "price_min": 100.0,
        "price_max": 300.5,
        "size_range": None,
        "make_time": 7,
        "sort_by": "recommend",
        "stock_required": None,
        "status": 1,
    }


def test_normalize_product_query_clears_invalid_type():
    result = normalize_product_query({"type": "unknown"})

    assert result["type"] is None
    assert result["sort_by"] == "recommend"
    assert result["status"] == 1


def test_normalize_ai_result_filters_values_by_candidates():
    request = build_custom_request()
    raw_data = {
        "purpose": "送礼",
        "style": "中式",
        "material": "木质",
        "budgetRange": "100-300",
        "size": "30cm 左右",
        "remark": "带礼盒",
        "colors": ["红色", "不存在的颜色", "金色", "红色"],
        "patterns": "祥云, 山水, 无效纹样",
        "aiRemark": "适合作为节日礼物",
    }

    result = normalize_ai_result(raw_data, request)

    assert result == {
        "purpose": "送礼",
        "style": "中式",
        "material": "木质",
        "budgetRange": "100-300",
        "size": "30cm 左右",
        "remark": "带礼盒",
        "colors": ["红色", "金色"],
        "patterns": ["祥云", "山水"],
        "aiRemark": "适合作为节日礼物",
    }


def test_ai_custom_request_normalizes_candidate_lists():
    request = AiCustomProductRequest(
        text="  定制一个送礼摆件  ",
        purposeList=["送礼", "送礼", " 自用 "],
        styleList="中式",
        materialList=["木质", "", "陶瓷"],
        budgetRangeList=["100-300"],
        colorList=["红色", None, "红色", " 金色 "],
        patternList=["祥云", "山水"],
    )

    assert request.text == "定制一个送礼摆件"
    assert request.purposeList == ["送礼", "自用"]
    assert request.styleList == ["中式"]
    assert request.materialList == ["木质", "陶瓷"]
    assert request.colorList == ["红色", "金色"]
