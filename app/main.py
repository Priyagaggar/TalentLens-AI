
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.endpoints import router as api_router
from app.api.auth import router as auth_router
from contextlib import asynccontextmanager
from app.db.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Safe database initialization on startup
    try:
        await init_db()
    except Exception as e:
        print(f"Warning: Database initialization skipped or failed: {e}")
    yield
    # Cleanup on shutdown can go here

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    # If we have a wildcard origin, we MUST NOT allow credentials, or browsers will block it.
    allow_credentials = True
    if "*" in settings.BACKEND_CORS_ORIGINS:
        allow_credentials = False

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API Router
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to the TalentLens AI API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
