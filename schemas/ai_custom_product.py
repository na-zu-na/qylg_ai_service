from typing import List,Optional, Union

from pydantic import BaseModel, Field, field_validator

class AiCustomProductRequest(BaseModel):
    text: str = Field(..., min_length=1, description="用户自然语言需求")
    purposeList: List[str] = Field(..., min_items=1, description="用途候选项")
    styleList: List[str] = Field(..., min_items=1, description="风格候选项")
    materialList: List[str] = Field(..., min_items=1, description="材质候选项")
    budgetRangeList: List[str] = Field(..., min_items=1, description="预算候选项")
    colorList: List[str] = Field(..., min_items=1, description="颜色候选项")
    patternList: List[str] = Field(..., min_items=1, description="纹样候选项")

    @field_validator("text")
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("text 不能为空")
        return value

    @field_validator(
        "purposeList",
        "styleList",
        "materialList",
        "budgetRangeList",
        "colorList",
        "patternList",
        mode="before"
    )
    def validate_candidate_list(cls, values: Union[List[str], str, None]) -> List[str]:
        if values is None:
            raise ValueError("候选项列表不能为空")

        # 👉 如果是单个字符串，转成 list
        if isinstance(values, str):
            values = [values]

        result = []
        seen = set()

        for item in values:
            if item is None:
                continue
            cleaned = str(item).strip()
            if not cleaned or cleaned in seen:
                continue
            result.append(cleaned)
            seen.add(cleaned)

        if not result:
            raise ValueError("候选项列表不能为空")

        return result



class AiCustomProductData(BaseModel):
    purpose: Optional[str] = Field(default=None)
    style: Optional[str] = Field(default=None)
    material: Optional[str] = Field(default=None)
    budgetRange: Optional[str] = Field(default=None)
    size: Optional[str] = Field(default=None)
    remark: Optional[str] = Field(default=None)
    colors: List[str] = Field(default_factory=list)
    patterns: List[str] = Field(default_factory=list),
    aiRemark: Optional[str] = Field(default=None)