from typing import Dict, Any

from openai import OpenAI
from core.config import settings
from core.exception import LLMInvokeError, AIResultParseError, AIResultValidationError
from schemas.ai_custom_product import AiCustomProductRequest
from utils.custom_product_util import build_prompt, normalize_ai_result
from utils.parser_util import extract_json_from_text

SYSTEM_PROMPT = """
你是一个严谨的中文定制订单信息提取助手。
你只能从候选项中选择已有值，不允许编造新值。
无法判断时返回 null。
只返回 JSON，不要解释，不要 markdown，不要多余文本。
""".strip()

class AICustomProductService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )

    def call_llm(self, prompt:str):
        try:
            completion=self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                temperature=0,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )

        except Exception as exc:
            raise LLMInvokeError(f"大模型调用失败: {exc}") from exc

        try:
            content = completion.choices[0].message.content
        except Exception as exc:
            raise LLMInvokeError("大模型返回为空") from exc

        if not content or not str(content).strip():
            raise LLMInvokeError("大模型返回为空")

        return str(content)


    def parse_custom_product(self, req:AiCustomProductRequest)->Dict[str,Any]:
        prompt=build_prompt(req)
        raw_content=self.call_llm(prompt)
        try:
            raw_data=extract_json_from_text(raw_content)
        except Exception as exc:
            raise AIResultParseError(f"模型结果解析失败: {exc}") from exc

        try:
            return normalize_ai_result(raw_data, req)
        except AIResultValidationError:
            raise
        except Exception as exc:
            raise AIResultValidationError(f"模型结果清洗失败: {exc}") from exc
