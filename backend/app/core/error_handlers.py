import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("uvicorn.error")

_STATUS_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    409: "conflict",
    422: "validation_error",
    429: "rate_limited",
    500: "internal_error",
    503: "service_unavailable",
}

def _envelope(
    request: Request,
    code: str,
    message: str,
    details: Optional[list[dict]] = None,
) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,  # only populated for validation errors
        },
        "request_id": getattr(request.state, "request_id", None),
        "path": request.url.path,
        "method": request.method,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc):
        """Wraps every HTTPException raised by services/routers into the
        standard envelope. Message text is preserved (clients validate on
        `error.code`, humans read `error.message`)."""
        code = _STATUS_CODES.get(exc.status_code, f"http_{exc.status_code}")
        message = exc.detail if isinstance(exc.detail, str) else "Request failed"
        headers = getattr(exc, "headers", None)
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(request, code, message),
            headers=headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc):
        details = [
            {
                "field": ".".join(str(loc) for loc in err["loc"][1:]) or "body",
                "message": err["msg"],
                "input": err.get("input"),
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=_envelope(request, "validation_error", "Validation failed", details),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """Last resort: log the traceback server-side, return a safe generic
        message. The request_id in the log matches the one in the response."""
        logger.exception(
            "Unhandled error on %s %s [request_id=%s]",
            request.method,
            request.url.path,
            getattr(request.state, "request_id", "?"),
        )
        return JSONResponse(
            status_code=500,
            content=_envelope(request, "internal_error", "Internal server error"),
        )