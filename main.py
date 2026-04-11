from fastapi import FastAPI,Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from api.routes_product_parse import router as parse_router
from core.config import settings
from api.routes_ai_custom_product import router as ai_custom_product_router
from core.exception import AppException

app = FastAPI(
    title="Qylg AI service",
    version="0.0.1"
)

app.include_router(parse_router,prefix="/api/parse",tags=["parse"])
app.include_router(ai_custom_product_router,prefix="/api/ai",tags=["ai"])

@app.exception_handler(AppException)
async def handle_app_exception(_: Request, exc: AppException):
    return JSONResponse(
        status_code=500,
        content={
            "code": exc.code,
            "msg": exc.message,
            "data": None,
        },
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_exception(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "msg": "请求参数校验失败",
            "data": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def handle_unknown_exception(_: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "msg": f"服务器内部错误: {exc}",
            "data": None,
        },
    )


@app.get("/health")
def health():
    return {
        "success": True,
        "message": "ok",
        "data": {
            "service": settings.APP_NAME,
            "env": settings.APP_ENV,
        },
    }
