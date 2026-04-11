import json
import re
from typing import Dict, Any


def extract_json_from_text(text: str) -> dict:
    """
    从模型输出中提取 JSON。
    兼容：
    - 纯 JSON
    - ```json ... ```
    - 前后有少量说明文字
    """
    text=text.strip()

    #去掉markdown的block
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    #直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    #提取最外层json
    match = re.search(r"\{.*?\}", text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return {}

    raise ValueError("无法从模型输出中提取有效 JSON")

def normalize_product_query(data:Dict[str,str]) -> Dict[str,Any]:
    """
    兜底清洗，保证字段存在且格式可用。
    """
    result = {
        "type": data.get("type"),
        "keyword": data.get("keyword"),
        "title": data.get("title"),
        "purpose": data.get("purpose"),
        "price_min": data.get("price_min"),
        "price_max": data.get("price_max"),
        "size_range": data.get("size_range"),
        "make_time": data.get("make_time"),
        "sort_by": data.get("sort_by") or "recommend",
        "stock_required": data.get("stock_required"),
        "status": 1 if data.get("status") is None else data.get("status"),
    }

    for key, value in result.items():
        if isinstance(value, str) and not value.strip():
            result[key] = None

    # 数值纠正
    if result["price_min"] is not None:
        result["price_min"] = float(result["price_min"])
    if result["price_max"] is not None:
        result["price_max"] = float(result["price_max"])
    if result["make_time"] is not None:
        result["make_time"] = int(result["make_time"])

    # 合法化 type
    if result["type"] not in ("mass", "custom", None):
        result["type"] = None

    # status 第一版固定只查上架
    result["status"] = 1

    return result