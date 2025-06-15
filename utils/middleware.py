from starlette.middleware.base import BaseHTTPMiddleware
from utils.logging import logger

class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        logger.info(
            "Incoming request",
            extra={
                "extra_fields": {
                          "headers": request.headers,
                          "method": request.method,
                          "url": str(request.url),
                          "status_code": response.status_code
                }
            },
        )
        return response
