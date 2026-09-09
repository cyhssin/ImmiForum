import os

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.error_handlers import register_error_handlers
from app.core.middleware import register_middleware
from app.core.openapi import build_custom_openapi

from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.seed import seed_roles
from app.routers import (
    auth,
    categories,
    comments,
    follows,
    moderation,
    questions,
    reactions,
    tags,
    users,
)

_DESCRIPTION = """
## Immiforum API

Community platform for immigrants: questions & answers, threaded discussion,
and a follow-based activity feed.

### Conventions
- **Base path:** `/api/v1` · **Auth:** Bearer JWT via the **Authorize** button (🔒)
- **Errors** always use one envelope:
  `{"error": {"code", "message", "details?"}, "request_id", "path", "method", "timestamp"}`
  — machine-readable `error.code` (`not_found`, `forbidden`, `validation_error`, ...),
  human-readable `error.message`, per-field `details[]` on 422
- **List endpoints** share the envelope `{"items", "total", "page", "size"}`
- **Moderation:** role-based — `moderator` (pin/close/delete content) and
  `admin` (user management) — every effective action is written to
  `GET /admin/moderation-logs`
- Correlate issues via the `X-Request-ID` response header
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_roles()
    yield

app = FastAPI(
    title="Immiforum API",
    version="1.0.0",
    description=_DESCRIPTION,
    openapi_tags=[
        {"name": "Auth", "description": "Registration, login (JWT), email verification."},
        {"name": "Questions", "description": "Question CRUD, search, tag/category filters, pagination. Pinned questions lead the global list."},
        {"name": "Comments", "description": "Unlimited-depth threaded comments per question."},
        {"name": "Likes & Bookmarks", "description": "Per-user toggles; counts always reflect reality."},
        {"name": "Users", "description": "Private dashboard (/users/me*) and public profiles/activity."},
        {"name": "Follows", "description": "Social graph and the personalized activity feed."},
        {"name": "Categories", "description": "Content organization."},
        {"name": "Tags", "description": "Free-form lowercase tags, auto-created from questions."},
        {"name": "Health", "description": "Service and database status."},
        {"name": "Admin & Moderation", "description": "Moderation actions and audit trail; user management (admin-only)."},
    ],
    swagger_ui_parameters={
        "persistAuthorization": True,      # token survives page refresh
        "displayRequestDuration": True,
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# CORS — configure via env, e.g. CORS_ORIGINS=http://localhost:3000,https://myforum.com
_origins = [
    o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

register_middleware(app)
register_error_handlers(app)
app.openapi = build_custom_openapi(app)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(questions.router, prefix=settings.API_V1_PREFIX)
app.include_router(categories.router, prefix=settings.API_V1_PREFIX)
app.include_router(tags.router, prefix=settings.API_V1_PREFIX)
app.include_router(comments.router, prefix=settings.API_V1_PREFIX)
app.include_router(reactions.router, prefix=settings.API_V1_PREFIX)
app.include_router(follows.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(moderation.router, prefix=settings.API_V1_PREFIX)

@app.get("/", include_in_schema=False)
def root():
    return {"message": "ImmiForum is running"}

@app.get("/health", tags=["Health"])
def health(db: Session = Depends(get_db)):
    """Liveness + database connectivity. Compose healthchecks can use this."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    return {"status": "ok", "database": db_status}