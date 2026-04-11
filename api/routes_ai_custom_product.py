import code

from fastapi import APIRouter
from openai.types.beta.threads import message

from schemas.ai_custom_product import AiCustomProductData, AiCustomProductRequest
from schemas.common import ApiResponse
from services.ai_custom_product_service import AICustomProductService

router = APIRouter()
ai_custom_product_service=AICustomProductService()

@router.post("/custom-product",response_model=ApiResponse[AiCustomProductData])
def custom_product(req: AiCustomProductRequest):
    result=ai_custom_product_service.parse_custom_product(req)
    return ApiResponse[AiCustomProductData](
        code=200,
        data=result,
        message="success"
    )