"""
Session Tracker Middleware

Detects user-exhaustion signals and returns a 429 SOVEREIGN_EXIT_REACHED
when repetition patterns cross the mandate threshold.
"""
import re
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

SESSION_TTL_MS = 24 * 60 * 60 * 1000
REPETITION_PATTERN = re.compile(r"\b(no\s*){3,}", re.IGNORECASE)
MAX_REPETITIONS = 3
LAST_TEXTS_WINDOW = 5

_sessions: dict = {}


def _purge_expired() -> None:
    now = time.time() * 1000
    expired = [sid for sid, state in _sessions.items() if now - state["last_request"] > SESSION_TTL_MS]
    for sid in expired:
        del _sessions[sid]


def _detect_repetition(texts: list) -> bool:
    if len(texts) < 3:
        return False
    last3 = [t.strip().lower() for t in texts[-3:]]
    return last3[0] == last3[1] == last3[2]


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


class SessionTrackerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method != "POST" or request.url.path.startswith("/api/sessions"):
            return await call_next(request)

        forwarded = request.headers.get("x-forwarded-for")
        client_ip = (
            forwarded.split(",")[0].strip()
            if forwarded
            else request.client.host if request.client else "anonymous"
        )
        session_id = request.headers.get("x-session-id") or client_ip
        now = time.time() * 1000

        _purge_expired()

        if session_id not in _sessions:
            _sessions[session_id] = {
                "attempts": 0,
                "repetitions": 0,
                "locked": False,
                "locked_at": None,
                "last_request": now,
                "last_texts": [],
            }
        session = _sessions[session_id]

        if session["locked"]:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "SOVEREIGN_EXIT_REACHED",
                    "message": "Transaction locked due to user exhaustion. Session must be unlocked or expire.",
                    "squealReport": {
                        "trigger": "User_Stop_Command",
                        "sessionId": session_id,
                        "repetitionCount": session["repetitions"],
                        "lockedAt": session["locked_at"],
                    },
                },
            )

        session["last_request"] = now
        session["attempts"] += 1

        body = await request.body()
        try:
            import json
            data = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            data = {}
        text = data.get("text") if isinstance(data, dict) else None

        if isinstance(text, str):
            session["last_texts"].append(text)
            if len(session["last_texts"]) > LAST_TEXTS_WINDOW:
                session["last_texts"].pop(0)
            if REPETITION_PATTERN.search(text):
                session["repetitions"] += 1
            if _detect_repetition(session["last_texts"]):
                session["repetitions"] += 1
            if session["repetitions"] >= MAX_REPETITIONS:
                session["locked"] = True
                session["locked_at"] = _now_iso()
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "SOVEREIGN_EXIT_REACHED",
                        "message": "Transaction locked: repeated exhaustion signals detected.",
                        "squealReport": {
                            "trigger": "User_Stop_Command",
                            "sessionId": session_id,
                            "repetitionCount": session["repetitions"],
                            "lockedAt": session["locked_at"],
                        },
                    },
                )

        async def receive():
            return {"type": "http.request", "body": body}

        request._receive = receive
        return await call_next(request)
