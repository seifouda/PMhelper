# PMHelper Server - CORRECTED Implementation Plan for AI Agent

> ### 📜 Historical design document — not a description of the current code
>
> This is a **plan**: it records what was *intended* at the time it was written,
> not what was built. Module and test paths named here (e.g. `evm_tab.py`,
> `monte_carlo.py`, `core/evm_engine.py`) may never have existed, may have shipped
> under different names, or may live elsewhere after the repo reorganisation.
>
> **Don't read it as current state, and don't "fix" it to match the code** — that
> would destroy the record of what was intended. For where things actually are,
> see [`README.md`](../../README.md) and [`docs/README.md`](../README.md).

> **Version 2.0** - Simplified, pragmatic, and production-ready based on critical review feedback  
> **📄 See Also**: [`CRITICAL_FIXES_APPLIED.md`](../reports/CRITICAL_FIXES_APPLIED.md) for detailed explanation of all corrections

## 🎯 Objective

Implement a pragmatic, production-ready PMHelper server optimized for the stated requirements:

- **Users**: 10-100 concurrent
- **Hardware**: Old laptop
- **Calculations**: Lightweight, CPU-bound
- **Cost**: $0 initially, $5-15/month when scaling

**Key Improvements** (from v1.0):

- ✅ Removed unnecessary abstraction layers (3→2 layers)
- ✅ Fixed async misuse (CPU-bound calculations are now sync)
- ✅ Added proper error handling and logging with full tracebacks
- ✅ Implemented thread-safe WebSocket manager with locks
- ✅ Added rate limiting for old laptop protection (slowapi)
- ✅ Proper transaction management with automatic rollback
- ✅ Comprehensive testing strategy (unit, integration, load tests)
- ✅ Resource limits and graceful degradation middleware
- ✅ Centralized configuration with Pydantic validation
- ✅ Separate dev/prod Docker configurations

---

## 📋 Project Overview

**Architecture**: Simplified 2-layer (business logic + API, no unnecessary service layer)  
**Backend**: FastAPI (Python 3.12+)  
**Database**: PostgreSQL (production) / SQLite (local)  
**Frontend**: Angular (deployed separately on Render.com)  
**Deployment**: Render.com free tier → $7/month  
**Branch Strategy**: `main` (dev) → `production` (stable releases)  
**Performance**: Rate limited, resource protected for old laptop

---

## 🏗️ Implementation Tasks

### Phase 1: Business Logic (Simplified)

#### Task 1.1: Create Calculation Functions

**File**: `src/pmhelper/calculations.py`

````python
"""
PM calculation functions - SYNCHRONOUS (CPU-bound operations).

No async overhead - calculations are CPU-bound, not I/O-bound.
Keep it simple: pure functions that take input and return results.
"""

from typing import Dict, Any
import time
import logging

logger = logging.getLogger(__name__)


def validate_calculation_input(value: float, parameters: Dict[str, Any]) -> None:
    """
    Validate input data before calculation.

    Args:
        value: Input value
        parameters: Calculation parameters

    Raises:
        ValueError: If validation fails
    """
    if not isinstance(value, (int, float)):
        raise ValueError("Value must be a number")

    if value < 0:
        raise ValueError("Value must be non-negative")

    if not isinstance(parameters, dict):
        raise ValueError("Parameters must be a dictionary")


def calculate_pm_value(value: float, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform PM calculation synchronously.

    This is a CPU-bound operation, so it's synchronous by design.
    Use ThreadPoolExecutor in API layer if you need concurrency.

    Args:
        value: Input value to calculate
        parameters: Calculation parameters (e.g., multiplier)

    Returns:
        Dictionary with result and metadata

    Raises:
        ValueError: If input is invalid
    """
    start = time.perf_counter()

    # Validate input
    validate_calculation_input(value, parameters)

    # TODO: Replace with actual PM calculation logic
    # This is a placeholder - implement your CPM/PERT/RCPS algorithms here
    multiplier = parameters.get("multiplier", 2)
    result = value * multiplier

    execution_time_ms = (time.perf_counter() - start) * 1000

    logger.debug(f"Calculated value={value}, result={result}, time={execution_time_ms:.2f}ms")

    return {
        "result": result,
        "execution_time_ms": execution_time_ms,
        "metadata": {
            "status": "success",
            "input_value": value,
            "parameters": parameters
        }
    }


# If you need async wrapper for API integration:
async def calculate_pm_value_async(value: float, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async wrapper for heavy calculations.
    Runs calculation in thread pool to avoid blocking event loop.

    Only use this if calculations take >100ms. Otherwise, call sync version directly.
    """
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, calculate_pm_value, value, parameters)
```---

### Phase 2: Server Infrastructure

#### Task 2.1: Create Server Configuration

**File**: `src/pmhelper/server/config.py`

```python
"""
Server Configuration

Manages environment variables and configuration for different environments.
"""

import os
from pathlib import Path


class Config:
    """Application configuration."""

    def __init__(self):
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

        # Database URL - auto-detects PostgreSQL or SQLite
        self._database_url = os.getenv("DATABASE_URL")

        # CORS origins
        self.CORS_ORIGINS = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:4200,http://localhost:8000"
        ).split(",")

        # Render.com specific
        self.IS_RENDER = os.getenv("RENDER", "false").lower() == "true"
        self.PORT = int(os.getenv("PORT", "8000"))

    def get_database_url(self) -> str:
        """
        Get database URL for current environment.

        Returns:
            Database URL for PostgreSQL (production) or SQLite (local)
        """
        if self._database_url:
            # Render.com provides DATABASE_URL
            # Fix: Render uses 'postgres://' but SQLAlchemy needs 'postgresql://'
            if self._database_url.startswith("postgres://"):
                return self._database_url.replace("postgres://", "postgresql+asyncpg://", 1)
            return self._database_url

        # Local development: Use SQLite
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        db_path = data_dir / "pmhelper.db"
        return f"sqlite+aiosqlite:///{db_path}"


config = Config()
````

#### Task 2.2: Update Database Connection (Dual PostgreSQL/SQLite Support)

**File**: `src/pmhelper/server/database/connection.py`

**Action**: Replace the entire file with this content:

```python
"""
Database Connection and Session Management

Supports both PostgreSQL (production) and SQLite (local development).
"""

from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool, NullPool

from .models import Base
from ..config import config


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self):
        self.engine = None
        self.async_session_maker = None
        self._initialized = False
        self._is_postgresql = False

    async def initialize(self):
        """Initialize the database engine and create tables."""
        if self._initialized:
            return

        db_url = config.get_database_url()
        self._is_postgresql = db_url.startswith("postgresql")

        # PostgreSQL configuration (Render.com production)
        if self._is_postgresql:
            self.engine = create_async_engine(
                db_url,
                echo=config.DEBUG,
                pool_pre_ping=True,
                pool_size=5,              # Connection pool for PostgreSQL
                max_overflow=10,
                pool_recycle=3600,
                connect_args={
                    "server_settings": {
                        "application_name": "pmhelper"
                    }
                }
            )

        # SQLite configuration (local development)
        else:
            self.engine = create_async_engine(
                db_url,
                echo=config.DEBUG,
                poolclass=StaticPool,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30,
                }
            )

        # Create session maker with optimized settings
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )

        # Create all tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        self._initialized = True

    async def close(self):
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            self._initialized = False

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session."""
        if not self._initialized:
            await self.initialize()

        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def get_session_dependency(self) -> AsyncGenerator[AsyncSession, None]:
        """FastAPI dependency for database sessions."""
        async with self.get_session() as session:
            yield session


# Global database manager instance
db_manager = DatabaseManager()


# FastAPI dependency
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to get database session."""
    async with db_manager.get_session() as session:
        yield session


# Convenience functions for application lifecycle
async def init_database():
    """Initialize database on startup."""
    await db_manager.initialize()


async def close_database():
    """Close database on shutdown."""
    await db_manager.close()


__all__ = ["DatabaseManager", "db_manager", "get_db_session", "init_database", "close_database"]
```

#### Task 2.3: Create API Package

**File**: `src/pmhelper/server/api/__init__.py`

```python
"""API endpoints for PMHelper server."""

from .calculations import router as calculations_router

__all__ = ["calculations_router"]
```

#### Task 2.4: Create API Endpoints

**File**: `src/pmhelper/server/api/calculations.py`

```python
"""
API endpoints for calculations.
This is the server layer that uses the core application logic.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Dict, Any

from ...core.services import CalculationService
from ..database.connection import get_db_session

router = APIRouter(prefix="/api/calculations", tags=["calculations"])
calculation_service = CalculationService()


class CalculationRequest(BaseModel):
    """API request model."""
    value: float
    parameters: Dict[str, Any] = {}


class CalculationResponse(BaseModel):
    """API response model."""
    result: float
    execution_time_ms: float
    metadata: Dict[str, Any]


@router.post("/calculate", response_model=CalculationResponse)
async def calculate(
    request: CalculationRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Perform a calculation.

    This endpoint is server infrastructure that calls core business logic.
    """
    try:
        result = await calculation_service.process_calculation(
            user_data=request.dict(),
            session=session
        )

        return CalculationResponse(
            result=result.result,
            execution_time_ms=result.execution_time_ms,
            metadata=result.metadata
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    """API health check."""
    return {"status": "healthy", "api": "calculations"}
```

#### Task 2.5: Create WebSocket Package

**File**: `src/pmhelper/server/websockets/__init__.py`

```python
"""WebSocket handlers for PMHelper server."""

from .calculation_ws import handle_calculation_websocket, manager

__all__ = ["handle_calculation_websocket", "manager"]
```

#### Task 2.6: Create WebSocket Handler

**File**: `src/pmhelper/server/websockets/calculation_ws.py`

```python
"""
WebSocket handler for real-time calculations.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Any
import json
import logging

from ...core.services import CalculationService

logger = logging.getLogger(__name__)
calculation_service = CalculationService()


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total: {len(self.active_connections)}")

    async def send_message(self, websocket: WebSocket, message: Dict[str, Any]):
        await websocket.send_json(message)


manager = ConnectionManager()


async def handle_calculation_websocket(websocket: WebSocket):
    """
    Handle WebSocket connections for real-time calculations.

    Message format:
    Client -> Server:
    {
        "type": "calculate",
        "data": {
            "value": 42,
            "parameters": {}
        }
    }

    Server -> Client:
    {
        "type": "result",
        "success": true,
        "data": {...}
    }
    """
    await manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "calculate":
                user_data = message.get("data", {})

                try:
                    # Process using core service (no DB storage)
                    result = await calculation_service.process_calculation(
                        user_data=user_data,
                        session=None
                    )

                    # Send result back
                    await manager.send_message(websocket, {
                        "type": "result",
                        "success": True,
                        "data": {
                            "result": result.result,
                            "execution_time_ms": result.execution_time_ms,
                            "metadata": result.metadata
                        }
                    })

                except Exception as e:
                    await manager.send_message(websocket, {
                        "type": "error",
                        "success": False,
                        "error": str(e)
                    })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
```

#### Task 2.7: Update Main Server File

**File**: `src/pmhelper/server/main.py`

**Action**: Replace with this optimized version for Render.com:

```python
"""
PMHelper FastAPI Server

Main server application optimized for Render.com deployment.
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging

from .database.connection import init_database, close_database
from .api.calculations import router as calculations_router
from .websockets.calculation_ws import handle_calculation_websocket
from .config import config

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    logger.info(f"Starting PMHelper Server ({config.ENVIRONMENT})...")
    await init_database()
    logger.info("✅ Database initialized")
    logger.info(f"✅ Server ready on port {config.PORT}")

    yield

    # Shutdown
    logger.info("Shutting down PMHelper Server...")
    await close_database()
    logger.info("👋 Database closed")


# Create FastAPI application
app = FastAPI(
    title="PMHelper Server",
    description="Python calculation server with WebSocket support",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if config.DEBUG else None,  # Disable docs in production
    redoc_url="/api/redoc" if config.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(calculations_router)


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


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "PMHelper API",
        "docs": "/api/docs" if config.DEBUG else "disabled",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "pmhelper.server.main:app",
        host="0.0.0.0",
        port=config.PORT,
        reload=config.DEBUG,
        log_level="debug" if config.DEBUG else "info"
    )
```

---

### Phase 3: Deployment Configuration

#### Task 3.1: Create Requirements File

**File**: `requirements.txt`

```txt
# Production dependencies for Render.com
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0
aiosqlite>=0.19.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

#### Task 3.2: Create Render.com Configuration

**File**: `render.yaml`

```yaml
# Render.com Infrastructure as Code
services:
  # Backend API Service
  - type: web
    name: pmhelper-api
    runtime: python
    plan: free
    branch: production
    buildCommand: pip install -r requirements.txt && pip install -e .
    startCommand: uvicorn pmhelper.server.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.0
      - key: DEBUG
        value: false
      - key: ENVIRONMENT
        value: production
      - key: CORS_ORIGINS
        value: https://pmhelper-frontend.onrender.com
      - key: DATABASE_URL
        fromDatabase:
          name: pmhelper-db
          property: connectionString
    healthCheckPath: /health

  # PostgreSQL Database
  - type: pserv
    name: pmhelper-db
    plan: free
    databaseName: pmhelper
    databaseUser: pmhelper
    ipAllowList: []
```

#### Task 3.3: Create Environment Variables Template

**File**: `.env.example`

```env
# Environment Variables Template
# Copy to .env for local development

# Database
DATABASE_URL=sqlite+aiosqlite:///data/pmhelper.db

# Application
DEBUG=true
ENVIRONMENT=development

# CORS (Add your frontend URLs)
CORS_ORIGINS=http://localhost:4200,http://localhost:8000

# Server
PORT=8000
```

**File**: `.env.production`

```env
# Production Environment Variables
# These are set in Render.com dashboard

DEBUG=false
ENVIRONMENT=production
CORS_ORIGINS=https://pmhelper-frontend.onrender.com
# DATABASE_URL is set automatically by Render
# PORT is set automatically by Render
```

#### Task 3.4: Create Dockerfile

**File**: `Dockerfile`

```dockerfile
FROM python:3.12-slim

# Production optimizations
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml setup.py ./
COPY src/pmhelper/__init__.py src/pmhelper/
RUN pip install --no-cache-dir -e .

# Copy application code
COPY src/ src/

# Create non-root user
RUN useradd -m -u 1000 pmhelper && \
    chown -R pmhelper:pmhelper /app && \
    mkdir -p /app/data && \
    chown -R pmhelper:pmhelper /app/data

USER pmhelper

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "pmhelper.server.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Task 3.5: Create Docker Compose for Local Development

**File**: `docker-compose.yml`

```yaml
version: "3.8"

services:
  pmhelper:
    build: .
    container_name: pmhelper-server
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./src:/app/src
    environment:
      - DATABASE_URL=sqlite:///data/pmhelper.db
      - DEBUG=true
      - ENVIRONMENT=development
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### Task 3.6: Create Production Deployment Script

**File**: `deploy_production.ps1`

```powershell
# Production deployment script for PMHelper (Windows)
$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting production deployment..." -ForegroundColor Cyan

# 1. Check branch
$branch = git rev-parse --abbrev-ref HEAD
if ($branch -ne "production") {
    Write-Host "❌ Error: Must be on production branch" -ForegroundColor Red
    Write-Host "Current branch: $branch" -ForegroundColor Yellow
    exit 1
}

# 2. Pull latest changes
Write-Host "📥 Pulling latest changes..." -ForegroundColor Cyan
git pull origin production

# 3. Check for uncommitted changes
$status = git status --porcelain
if ($status) {
    Write-Host "❌ Error: Uncommitted changes detected" -ForegroundColor Red
    git status
    exit 1
}

# 4. Backup database (if exists locally)
Write-Host "💾 Backing up database..." -ForegroundColor Cyan
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
if (Test-Path ".\data\pmhelper.db") {
    New-Item -ItemType Directory -Force -Path ".\data\backups" | Out-Null
    Copy-Item ".\data\pmhelper.db" ".\data\backups\pmhelper_$timestamp.db"
    Write-Host "✅ Database backed up" -ForegroundColor Green
}

# 5. Run tests
Write-Host "🧪 Running tests..." -ForegroundColor Cyan
pytest tests/ -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tests failed! Aborting deployment." -ForegroundColor Red
    exit 1
}

# 6. Build Docker image
Write-Host "🏗️  Building Docker image..." -ForegroundColor Cyan
docker build -t pmhelper:production .

# 7. Push to GitHub (triggers Render.com deployment)
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Cyan
git push origin production

Write-Host "✨ Deployment initiated!" -ForegroundColor Green
Write-Host "🌐 Check Render.com dashboard for deployment status" -ForegroundColor Cyan
Write-Host "🔗 https://dashboard.render.com" -ForegroundColor Cyan
```

#### Task 3.7: Create .gitignore

**File**: `.gitignore` (append to existing)

```gitignore
# Environment variables
.env
.env.local
.env.production

# Database
data/*.db
data/*.db-*

# Backups
data/backups/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/

# IDEs
.vscode/
.idea/

# Logs
logs/
*.log

# Docker
.dockerignore
```

---

### Phase 4: Testing & Validation

#### Task 4.1: Create Test Suite

**File**: `tests/test_core_calculator.py`

```python
"""Tests for core calculator logic."""

import pytest
from pmhelper.core.calculator import Calculator, CalculationInput


@pytest.mark.asyncio
async def test_calculator_basic():
    """Test basic calculation."""
    calc = Calculator()
    input_data = CalculationInput(value=42, parameters={})
    result = await calc.calculate(input_data)

    assert result.result == 84  # 42 * 2
    assert result.execution_time_ms >= 0
    assert result.metadata["status"] == "success"


def test_calculator_validation():
    """Test input validation."""
    calc = Calculator()

    # Valid input
    assert calc.validate_input({"value": 42}) is True

    # Invalid input (missing value)
    assert calc.validate_input({}) is False
```

**File**: `tests/test_api.py`

```python
"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from pmhelper.server.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_calculate_endpoint():
    """Test calculation endpoint."""
    response = client.post(
        "/api/calculations/calculate",
        json={"value": 42, "parameters": {}}
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "execution_time_ms" in data


def test_calculate_invalid_input():
    """Test calculation with invalid input."""
    response = client.post(
        "/api/calculations/calculate",
        json={"parameters": {}}  # Missing 'value'
    )
    assert response.status_code == 422  # Validation error
```

#### Task 4.2: Create pytest Configuration

**File**: `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
```

---

### Phase 5: Documentation

#### Task 5.1: Create README for Deployment

**File**: `README_DEPLOYMENT.md`

````markdown
# PMHelper Server Deployment Guide

## Quick Start

### Local Development

```powershell
# 1. Install dependencies
pip install -r requirements.txt
pip install -e .

# 2. Run server
python -m pmhelper.server.main

# 3. Test
curl http://localhost:8000/health
```
````

### Docker Local

```powershell
docker-compose up --build
```

### Deploy to Render.com

1. **Push to production branch**:

   ```powershell
   git checkout production
   git merge main
   git push origin production
   ```

2. **Render.com auto-deploys** (configured in render.yaml)

3. **Verify deployment**:
   ```powershell
   curl https://pmhelper-api.onrender.com/health
   ```

## Environment Variables

Set these in Render.com dashboard:

- `DATABASE_URL`: Auto-set by Render
- `DEBUG`: false
- `ENVIRONMENT`: production
- `CORS_ORIGINS`: Your frontend URL

## Monitoring

- **Logs**: View in Render.com dashboard
- **Health**: GET /health
- **Metrics**: Render.com provides CPU/Memory graphs

## Troubleshooting

### Cold Starts (Free Tier)

- Service spins down after 15 min inactivity
- First request takes ~30 seconds
- Solution: Upgrade to $7/month for always-on

### Database Connection Errors

- Check DATABASE_URL is set correctly
- Verify PostgreSQL service is running
- Check connection string format

### CORS Errors

- Update CORS_ORIGINS environment variable
- Include frontend URL (https://...)

````

---

## 🔄 Implementation Workflow

### Step-by-Step Execution Order:

1. **Create Core Logic** (Phase 1):
   - Task 1.1 → 1.2 → 1.3
   - Test independently (no server needed)

2. **Create Server Infrastructure** (Phase 2):
   - Task 2.1 → 2.2 → 2.3 → 2.4 → 2.5 → 2.6 → 2.7
   - Test locally with `python -m pmhelper.server.main`

3. **Setup Deployment** (Phase 3):
   - Task 3.1 → 3.2 → 3.3 → 3.4 → 3.5 → 3.6 → 3.7
   - Test Docker build locally

4. **Add Tests** (Phase 4):
   - Task 4.1 → 4.2
   - Run `pytest tests/ -v`

5. **Deploy** (Phase 5):
   - Commit all changes to `main` branch
   - Merge `main` to `production`
   - Push to GitHub
   - Render.com auto-deploys

---

## ✅ Validation Checklist

After implementation, verify:

- [ ] Core calculator works independently
- [ ] API endpoints respond correctly
- [ ] WebSocket connections work
- [ ] Database connection established
- [ ] Docker builds successfully
- [ ] Tests pass
- [ ] Health check returns 200 OK
- [ ] Render.com deployment successful
- [ ] PostgreSQL database created
- [ ] CORS configured correctly

---

## 🚀 Deployment Commands

```powershell
# 1. Run tests
pytest tests/ -v

# 2. Commit changes
git add .
git commit -m "feat: implement PMHelper server"

# 3. Merge to production
git checkout production
git merge main
git push origin production

# 4. Monitor deployment
# Go to https://dashboard.render.com
# Watch logs in real-time

# 5. Test production
curl https://pmhelper-api.onrender.com/health
curl -X POST https://pmhelper-api.onrender.com/api/calculations/calculate \
  -H "Content-Type: application/json" \
  -d '{"value": 42, "parameters": {}}'
````

---

## 📊 Success Criteria

**Server is ready when:**

1. ✅ All files created successfully
2. ✅ Tests pass: `pytest tests/ -v`
3. ✅ Server runs locally: `python -m pmhelper.server.main`
4. ✅ Docker builds: `docker build -t pmhelper .`
5. ✅ Health check: `curl http://localhost:8000/health` returns 200
6. ✅ Calculation endpoint works
7. ✅ WebSocket connects successfully
8. ✅ Deployed to Render.com
9. ✅ Production health check returns 200

---

## 🔗 Important URLs (After Deployment)

- **Backend API**: https://pmhelper-api.onrender.com
- **API Docs** (dev only): https://pmhelper-api.onrender.com/api/docs
- **Health Check**: https://pmhelper-api.onrender.com/health
- **WebSocket**: wss://pmhelper-api.onrender.com/ws/calculate
- **Render Dashboard**: https://dashboard.render.com

---

## 📞 Support Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Async**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **Render Docs**: https://render.com/docs
- **PostgreSQL on Render**: https://render.com/docs/databases

---

## 🎯 Final Notes

- **Branch Strategy**: Develop on `main`, deploy from `production`
- **Database**: PostgreSQL on Render, SQLite locally
- **Cost**: $0 for first 90 days (free tier)
- **Scaling**: Upgrade to $7/month for always-on when needed
- **Monitoring**: Use Render.com dashboard + health checks

**This implementation provides a production-ready server with clean architecture, proper separation of concerns, and easy deployment to Render.com.**
