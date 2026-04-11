from fastapi import APIRouter, HTTPException

from schemas.common import ApiResponse
from schemas.product_request import ProductQueryParseRequest
from schemas.products_response import ProductQueryData
from services.product_parser_service import ProductParserService

router = APIRouter()
parser_service =ProductParserService()

@router.post("/product-query", response_model=ApiResponse[ProductQueryData])
def parse_product_query(req: ProductQueryParseRequest):
    try:
        result=parser_service.parse_product_query(req.text)
        return ApiResponse[ProductQueryData](
            code=200,
            message="success",
            data=ProductQueryData(**result)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"商品查询解析失败: {str(e)}")