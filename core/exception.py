class AppException(Exception):
    def __init__(self, message: str, code: int = 500):
        super().__init__(message)
        self.message = message
        self.code = code


class LLMInvokeError(AppException):
    def __init__(self, message: str = "大模型调用失败"):
        super().__init__(message=message, code=5001)


class AIResultParseError(AppException):
    def __init__(self, message: str = "模型结果解析失败"):
        super().__init__(message=message, code=5002)


class AIResultValidationError(AppException):
    def __init__(self, message: str = "模型结果清洗失败"):
        super().__init__(message=message, code=5003)
