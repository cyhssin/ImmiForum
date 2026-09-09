import uuid

from starlette.requests import Request

def register_middleware(app) -> None:
    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        """Correlation ID per request: honored from X-Request-ID, else minted.
        Echoed on every response and embedded in error envelopes."""
        rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
        request.state.request_id = rid
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response