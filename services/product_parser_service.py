from core.config import settings
from openai import OpenAI
from utils.parser_util import extract_json_from_text, normalize_product_query


SYSTEM_PROMPT = """
你是一个电商商品搜索条件提取助手。
你的任务是把用户的自然语言购买需求，提取成结构化商品查询条件。

你只允许返回 JSON。
不要返回解释，不要返回 markdown，不要返回多余文字。

商品表字段参考：
- type: 商品类型，mass=普通商品，custom=定制商品
- title: 标题
- price: 现价
- min_price: 价格区间下限
- max_price: 价格区间上限
- anchor: 简介
- description: 详细描述
- purpose: 用途
- stock: 库存
- size_range: 尺寸范围，可选值常见为：
  - 小型摆件
  - 大型陈设
  - 小型摆件和大型陈设均可
- make_time: 制作时间，单位天
- status: 状态，0=下架，1=上架

请你输出以下 JSON 字段：
{
  "type": null,
  "keyword": null,
  "title": null,
  "purpose": null,
  "price_min": null,
  "price_max": null,
  "size_range": null,
  "make_time": null,
  "sort_by": "default",
  "status": 1
}

规则：
1. 如果用户说“定制”“私人定做”“专属制作”等，type 输出 custom。
2. 如果用户明确说普通现货、现成礼物、直接买，type 输出 mass。
3. keyword 用于概括商品关键词，尽量简洁，可用于标题/描述检索。
4. title 只有在用户明确点名某类标题时才填，否则为 null。
5. purpose 提取使用目的，如“送礼”“客厅装饰”“生日礼物”。
6. price_min / price_max 按用户预算提取，没有就为 null。
7. size_range 只在用户明确提到大小、摆件/陈设时提取。
8. make_time 只在用户明确提到制作周期、几天做好时提取。
9. status 固定返回 1。
10. 不确定的字段返回 null，不要猜测。
"""


class ProductParserService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )

    def parse_product_query(self, user_text: str) -> dict:
        user_prompt = f"""
                        用户输入：
                        {user_text}
                        
                        请严格返回 JSON。
                        """

        completion = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = completion.choices[0].message.content
        raw_data = extract_json_from_text(content)
        return normalize_product_query(raw_data)