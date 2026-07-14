"""
PMHelper FastAPI Server

Main server application optimized for Render.com deployment.
Serves the Angular Edu web app from /static and the API from /api/*.
"""

from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
import logging

from .database.connection import init_database, close_database
from .api.routes.web import router as web_router, limiter
from .websockets.calculation_ws import handle_calculation_websocket
from .config import config

# Legacy calculations router — may not be importable in web-only deploys
try:
    from .api.routes.calculations import router as calculations_router
except ImportError:
    calculations_router = None

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Resolve the static directory (Angular build output)
STATIC_DIR = Path(__file__).resolve().parent.parent.parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    logger.info(f"Starting PMHelper Server ({config.ENVIRONMENT})...")
    try:
        await init_database()
        logger.info("✅ Database initialized")
    except Exception as exc:
        logger.warning(f"⚠️  Database init skipped ({exc})")
    logger.info(f"✅ Server ready on port {config.PORT}")

    yield

    # Shutdown
    logger.info("Shutting down PMHelper Server...")
    try:
        await close_database()
    except Exception:
        pass
    logger.info("👋 Server stopped")


# Create FastAPI application
app = FastAPI(
    title="PMHelper Server",
    description="Python calculation server with WebSocket support",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if config.DEBUG else None,
    redoc_url="/api/redoc" if config.DEBUG else None,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS — only needed during local development (Angular DevServer on :4200)
if config.DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routers
if calculations_router is not None:
    app.include_router(calculations_router)
app.include_router(web_router)


# WebSocket endpoint
@app.websocket("/ws/calculate")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time calculations."""
    await handle_calculation_websocket(websocket)


# Health check endpoint (for Render.com monitoring)
@app.get("/health")
async def health_check():
    """Server health check."""
    return {
        "status": "healthy",
        "service": "pmhelper",
        "version": "1.0.0",
        "environment": config.ENVIRONMENT
    }


# ── Serve Angular SPA ───────────────────────────────────────────────────────
# Mount static assets (JS, CSS, images). The `html=True` flag serves
# index.html for directory roots, but we still need an explicit fallback
# for deep links (e.g. /network, /gantt) so Angular's router can handle them.

if STATIC_DIR.is_dir():
    @app.get("/{full_path:path}")
    async def spa_fallback(request: Request, full_path: str):
        """Serve static files or fall back to index.html for SPA routing."""
        file_path = (STATIC_DIR / full_path).resolve()
        if full_path and file_path.is_relative_to(
                STATIC_DIR) and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
else:
    @app.get("/")
    async def root():
        return {"message": "PMHelper API", "docs": "/api/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "pmhelper.server.main:app",
        host="0.0.0.0",
        port=config.PORT,
        reload=config.DEBUG,
        log_level="debug" if config.DEBUG else "info"
    )
