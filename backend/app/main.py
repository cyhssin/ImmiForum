from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.db.seed import seed_roles
from app.routers import auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    seed_roles()
    yield
    # Shutdown (if needed)

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {"message": "Immigrant Forum"}
