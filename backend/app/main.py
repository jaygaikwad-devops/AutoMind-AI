"""AutoMind AI — FastAPI entrypoint."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, videos, social, agents, workflows, analytics, ws


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init DB pools, Redis, etc.
    yield
    # Shutdown


app = FastAPI(
    title="AutoMind AI",
    version="3.0.0",
    description="Autonomous AI Marketing OS — backend",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(videos.router, prefix="/api/videos", tags=["videos"])
app.include_router(social.router, prefix="/api/social", tags=["social"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(ws.router, prefix="/ws", tags=["ws"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "automind-api"}
