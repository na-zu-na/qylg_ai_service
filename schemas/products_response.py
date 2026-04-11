from pydantic import BaseModel,Field
from typing import Optional,Any,Literal

from schemas.common import ApiResponse


class ProductQueryData(BaseModel):
    type: Optional[Literal["mass", "custom"]] = Field(default=None, description="商品类型")
    keyword: Optional[str] = Field(default=None, description="商品关键词，通常用于匹配标题或描述")
    title: Optional[str] = Field(default=None, description="明确商品标题")
    purpose: Optional[str] = Field(default=None, description="用途，例如送礼、客厅装饰")
    price_min: Optional[float] = Field(default=None, description="用户期望最低价格")
    price_max: Optional[float] = Field(default=None, description="用户期望最高价格")
    size_range: Optional[str] = Field(default=None, description="尺寸范围，如小型摆件、大型陈设")
    make_time: Optional[int] = Field(default=None, description="可接受制作时间，单位天")
    sort_by: Optional[str] = Field(default="default", description="排序方式")
    status: Optional[int] = Field(default=1, description="默认只查上架商品")

    class Config:
        json_schema_extra={
            "example": {
                "type": "mass",
                "keyword": "木质新中式摆件",
                "title": None,
                "purpose": "送女生礼物",
                "price_min": None,
                "price_max": 200,
                "size_range": "小型摆件",
                "make_time": None,
                "sort_by": "recommend",
                "status": 1
            }
        }