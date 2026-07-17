"""
Tracing Middleware

Per-request trace IDs via contextvars.
"""
import re
import contextvars
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

TRACE_CONTEXT: contextvars.ContextVar = contextvars.ContextVar(
    "trace_context", default={"traceId": "no-trace", "startTime": 0}
)
SAFE_TRACE_ID = re.compile(r"^[\x20-\x7E]{1,200}$")


class TracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        incoming_id = request.headers.get("x-trace-id")
        trace_id = (
            incoming_id
            if incoming_id and SAFE_TRACE_ID.match(incoming_id)
            else str(uuid.uuid4())
        )
        token = TRACE_CONTEXT.set({"traceId": trace_id, "startTime": time.time()})
        try:
            response = await call_next(request)
            response.headers["X-Trace-Id"] = trace_id
            return response
        finally:
            TRACE_CONTEXT.reset(token)


def get_trace_id() -> str:
    return TRACE_CONTEXT.get({}).get("traceId", "no-trace")
