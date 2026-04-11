from core.exception import AIResultValidationError
from schemas.ai_custom_product import AiCustomProductRequest
import json
from typing import Any, Dict, Iterable, Optional, List


def build_prompt(req:AiCustomProductRequest)->str:
    required_schema = {
        "purpose": "string or null",
        "style": "string or null",
        "material": "string or null",
        "budgetRange": "string or null",
        "size": "string or null",
        "remark": "string or null",
        "colors": ["string"],
        "patterns": ["string"],
        "aiRemark":"string or null"
    }

    return f"""
    你是一个“定制订单字段提取助手”，请根据用户自然语言需求，提取结构化下单信息。

    必须严格遵守以下规则：
    1. purpose 只能从 purposeList 中选择
    2. style 只能从 styleList 中选择，如果无法判断可以自行选择一个合适的
    3. material 只能从 materialList 中选择，如果无法判断可以自行选择一个合适的
    4. budgetRange 只能从 budgetRangeList 中选择，如果无法判断可以自行选择一个合适的
    5. colors 只能从 colorList 中选择，如果无法判断可以自行选择一个合适的
    6. patterns 只能从 patternList 中选择，如果无法判断可以自行选择一个合适的
    7. 不能编造候选项之外的新值
    8. 如果无法判断，除单独提及的字段外单值字段返回 null
    9. colors 和 patterns 必须返回数组，最多 3 个，且不能重复
    10. size 和 remark 可以是自由文本；你可以根据实际情况或输入填写，无法判断返回 null
    11. 所有字段必须存在
    12.aiRemark可以给出一句解释为什么这么选，但要简单
    13. 只返回 JSON，不要解释，不要 markdown，不要额外文字

    用户输入：
    {req.text}

    候选项：
    purposeList = {json.dumps(req.purposeList, ensure_ascii=False)}
    styleList = {json.dumps(req.styleList, ensure_ascii=False)}
    materialList = {json.dumps(req.materialList, ensure_ascii=False)}
    budgetRangeList = {json.dumps(req.budgetRangeList, ensure_ascii=False)}
    colorList = {json.dumps(req.colorList, ensure_ascii=False)}
    patternList = {json.dumps(req.patternList, ensure_ascii=False)}

    你必须返回如下结构的 JSON：
    {json.dumps(required_schema, ensure_ascii=False)}
    """.strip()

def normalize_ai_result(raw_data: Dict[str, Any], req: AiCustomProductRequest) -> Dict[str, Any]:
    if not isinstance(raw_data, dict):
        raise AIResultValidationError("模型返回结果不是 JSON 对象")

    result = {
        "purpose": pick_valid_value(raw_data.get("purpose"), req.purposeList),
        "style": pick_valid_value(raw_data.get("style"), req.styleList),
        "material": pick_valid_value(raw_data.get("material"), req.materialList),
        "budgetRange": pick_valid_value(raw_data.get("budgetRange"), req.budgetRangeList),
        "size": _normalize_text(raw_data.get("size")),
        "remark": _normalize_text(raw_data.get("remark")),
        "colors": pick_valid_list(raw_data.get("colors"), req.colorList, max_items=3),
        "patterns": pick_valid_list(raw_data.get("patterns"), req.patternList, max_items=3),
        "aiRemark": _normalize_text(raw_data.get("aiRemark")),
    }

    return result

#转换为str
def _normalize_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    value = str(value).strip()
    return value or None

#校验单个元素
def pick_valid_value(value: Any, candidates: Iterable[str]) -> Optional[str]:
    normalized = _normalize_text(value)
    if normalized is None:
        return None

    candidate_map = {item.strip(): item.strip() for item in candidates if item and item.strip()}
    if normalized in candidate_map:
        return candidate_map[normalized]

    lower_map = {item.lower(): item for item in candidate_map.values()}
    return lower_map.get(normalized.lower())

#校验多个元素
def pick_valid_list(values: Any, candidates: Iterable[str], max_items: int = 3) -> List[str]:
    candidate_map = {item.strip(): item.strip() for item in candidates if item and item.strip()}
    lower_map = {item.lower(): item for item in candidate_map.values()}

    if values is None:
        raw_items = []
    elif isinstance(values, list):
        raw_items = values
    else:
        text = str(values).replace("，", ",").replace("、", ",")
        raw_items = [part.strip() for part in text.split(",")]

    result = []
    seen = set()

    for item in raw_items:
        normalized = _normalize_text(item)
        if normalized is None:
            continue

        final_value = candidate_map.get(normalized) or lower_map.get(normalized.lower())
        if not final_value or final_value in seen:
            continue

        result.append(final_value)
        seen.add(final_value)

        if len(result) >= max_items:
            break

    return result