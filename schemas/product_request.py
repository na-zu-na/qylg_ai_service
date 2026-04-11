from pydantic import Field, BaseModel


class ProductQueryParseRequest(BaseModel):
    text: str = Field(..., min_length=1, description="用户自然语言商品查询内容")