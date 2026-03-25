"""
PMHelper FastAPI Application

Main FastAPI application for PMHelper server mode.
Provides REST API access to PMHelper analysis engines.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
from typing import Dict, Any

from ..config import config
from ..database.connection import init_database, close_database
from .routes import projects, analysis, selection


# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting PMHelper Server...")
    await init_database()
    logger.info(f"Server running at {config.get_server_url()}")
    logger.info(f"API documentation at {config.get_docs_url()}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down PMHelper Server...")
    await close_database()
    logger.info("Server shutdown complete.")


# Create FastAPI application
app = FastAPI(
    title="PMHelper API",
    description="REST API for Project Management Analysis using CPM, PERT, and RCPS methods",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response


# Exception handler for uncaught exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception for {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "detail": str(exc) if config.DEBUG else None
        }
    )


# Root endpoint
@app.get("/", tags=["General"])
async def root() -> Dict[str, Any]:
    """Welcome endpoint with API information."""
    return {
        "message": "Welcome to PMHelper API",
        "version": "1.0.0",
        "description": "REST API for Project Management Analysis",
        "features": [
            "Critical Path Method (CPM) analysis",
            "Program Evaluation and Review Technique (PERT)",
            "Resource-Constrained Project Scheduling (RCPS)",
            "Project Selection (AHP, Linear Scoring, B/C, Portfolio)",
            "Project crashing optimization",
            "Network diagrams and visualizations"
        ],
        "documentation": {
            "swagger_ui": f"{config.get_server_url()}/docs",
            "redoc": f"{config.get_server_url()}/redoc"
        },
        "endpoints": {
            "projects": "/api/projects",
            "analysis": "/api/analyze",
            "selection": "/api/selection",
            "jobs": "/api/jobs",
            "health": "/health"
        }
    }


# Health check endpoint
@app.get("/health", tags=["General"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "server": {
            "host": config.HOST,
            "port": config.PORT,
            "debug": config.DEBUG
        },
        "database": "connected",  # TODO: Add actual database health check
        "version": "1.0.0"
    }


# API version endpoint
@app.get("/api/version", tags=["General"])
async def api_version() -> Dict[str, str]:
    """Get API version information."""
    return {
        "api_version": "1.0.0",
        "pmhelper_version": "1.0.0",
        "supported_analyses": ["cpm", "pert", "rcps", "ahp", "linear_scoring", "benefit_cost", "portfolio"]
    }


# Include routers
app.include_router(projects.router, prefix="/api", tags=["Projects"])
app.include_router(analysis.router, prefix="/api", tags=["Analysis"])
app.include_router(selection.router, prefix="/api", tags=["Selection"])


# Server info for debugging
if config.DEBUG:
    @app.get("/debug/info", tags=["Debug"], include_in_schema=False)
    async def debug_info():
        """Debug information (only available in debug mode)."""
        return {
            "config": {
                "host": config.HOST,
                "port": config.PORT,
                "database_url": config.DATABASE_URL,
                "debug": config.DEBUG,
                "log_level": config.LOG_LEVEL
            },
            "cors_origins": config.CORS_ORIGINS,
            "performance": {
                "max_workers": config.MAX_WORKERS,
                "max_concurrent_analyses": config.MAX_CONCURRENT_ANALYSES,
                "request_timeout": config.REQUEST_TIMEOUT
            }
        }


__all__ = ["app"]