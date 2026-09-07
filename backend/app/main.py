from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.db.seed import seed_roles
from app.routers import admin, auth, categories, questions, tags

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_roles()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
app.include_router(questions.router, prefix=settings.API_V1_PREFIX)
app.include_router(categories.router, prefix=settings.API_V1_PREFIX)
app.include_router(tags.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {"message": "Forum API is running"}