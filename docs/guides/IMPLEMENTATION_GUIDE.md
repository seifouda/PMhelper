# PMHelper Server Implementation Guide

## Quick Start

This guide provides step-by-step instructions to implement the PMHelper server architecture with separation of concerns.

## Prerequisites

- Python 3.12+
- Docker Desktop (for Windows)
- Node.js 18+ (for Angular)
- Git

## Project Structure Overview

```
PMhelper/
├── src/pmhelper/
│   ├── core/                    # Business Logic (Independent)
│   │   ├── __init__.py
│   │   ├── calculator.py
│   │   ├── models.py
│   │   └── services.py
│   │
│   └── server/                  # Server Infrastructure
│       ├── main.py
│       ├── config.py
│       ├── api/
│       │   └── calculations.py
│       ├── database/
│       │   ├── connection.py    # ✅ Already exists (optimized)
│       │   └── models.py
│       └── websockets/
│           └── calculation_ws.py
│
├── web/                        # Angular app
├── data/                        # Runtime data
├── docker-compose.yml
└── Dockerfile
```

## Step 1: Update Database Connection (Already Done)

The `connection.py` file needs to be optimized for old laptop hardware.

**File**: `src/pmhelper/server/database/connection.py`

### Changes needed:

```python
# Add to initialize() method:
self.engine = create_async_engine(
    config.get_database_url(),
    echo=config.DEBUG,
    poolclass=StaticPool,
    pool_pre_ping=True,      # ← ADD: Verify connections
    pool_recycle=3600,       # ← ADD: Recycle connections
    connect_args={
        "check_same_thread": False,
        "timeout": 30,       # ← ADD: Increase timeout for old laptop
    }
)

# Update session maker:
self.async_session_maker = async_sessionmaker(
    self.engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False          # ← ADD: Reduce DB operations
)
```

## Step 2: Create Core Application Layer

### 2.1 Core Package Init

**File**: `src/pmhelper/core/__init__.py`

```python
"""
PMHelper Core Application Logic

This package contains all business logic and calculations,
independent of the server infrastructure.
"""

from .calculator import Calculator
from .services import CalculationService

__all__ = ["Calculator", "CalculationService"]
```

### 2.2 Calculator (Pure Logic)

**File**: `src/pmhelper/core/calculator.py`

```python
"""
Core calculation engine for PMHelper.
Contains all PM-related calculations independent of server logic.
"""

from typing import Dict, Any
from dataclasses import dataclass
import time


@dataclass
class CalculationInput:
    """Input data for calculations."""
    value: float
    parameters: Dict[str, Any]


@dataclass
class CalculationResult:
    """Result of a calculation."""
    result: float
    metadata: Dict[str, Any]
    execution_time_ms: float


class Calculator:
    """
    Pure calculation logic - no server dependencies.
    This can be tested independently and reused elsewhere.
    """

    def __init__(self):
        pass

    async def calculate(self, input_data: CalculationInput) -> CalculationResult:
        """
        Perform the main calculation.

        Args:
            input_data: Input parameters for calculation

        Returns:
            CalculationResult with computed values
        """
        start = time.time()

        # YOUR CALCULATION LOGIC HERE
        # Example: Replace with your actual PM calculations
        result = input_data.value * 2

        execution_time = (time.time() - start) * 1000

        return CalculationResult(
            result=result,
            metadata={"status": "success"},
            execution_time_ms=execution_time
        )

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data before calculation."""
        required_fields = ["value"]
        return all(field in input_data for field in required_fields)
```

### 2.3 Service Layer

**File**: `src/pmhelper/core/services.py`

```python
"""
Business logic services for PMHelper.
Orchestrates calculations and data operations.
"""

from typing import Dict, Any, Optional
from .calculator import Calculator, CalculationInput, CalculationResult


class CalculationService:
    """
    Service layer that orchestrates calculations.
    Can interact with database through dependency injection.
    """

    def __init__(self):
        self.calculator = Calculator()

    async def process_calculation(
        self,
        user_data: Dict[str, Any],
        session: Optional[Any] = None
    ) -> CalculationResult:
        """
        Process a calculation request with optional database storage.

        Args:
            user_data: Raw user input
            session: Optional database session for storing results

        Returns:
            CalculationResult
        """
        # Validate input
        if not self.calculator.validate_input(user_data):
            raise ValueError("Invalid input data")

        # Create input object
        calc_input = CalculationInput(
            value=user_data.get("value", 0),
            parameters=user_data.get("parameters", {})
        )

        # Perform calculation
        result = await self.calculator.calculate(calc_input)

        # Optionally store in database
        if session:
            await self._store_result(session, user_data, result)

        return result

    async def _store_result(self, session, input_data, result):
        """Store calculation result in database."""
        # TODO: Implement database storage
        pass
```

## Step 3: Create API Layer

### 3.1 API Package Init

**File**: `src/pmhelper/server/api/__init__.py`

```python
"""API endpoints for PMHelper server."""

from .calculations import router as calculations_router

__all__ = ["calculations_router"]
```

### 3.2 Calculation Endpoints

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

## Step 4: Create WebSocket Layer

### 4.1 WebSocket Package Init

**File**: `src/pmhelper/server/websockets/__init__.py`

```python
"""WebSocket handlers for PMHelper server."""

from .calculation_ws import handle_calculation_websocket, manager

__all__ = ["handle_calculation_websocket", "manager"]
```

### 4.2 WebSocket Handler

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

## Step 5: Update Main Server File

**File**: `src/pmhelper/server/main.py`

```python
"""
PMHelper FastAPI Server

Main server application that integrates all components.
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    logger.info("Starting PMHelper Server...")
    await init_database()
    logger.info("✅ Database initialized")
    logger.info("✅ Server ready on http://localhost:8000")

    yield

    # Shutdown
    logger.info("Shutting down PMHelper Server...")
    await close_database()
    logger.info("👋 Database closed")


# Create FastAPI application
app = FastAPI(
    title="PMHelper Server",
    description="Python calculation server with WebSocket support for Angular frontend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for Angular development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",  # Angular dev server
        "http://localhost:8000",  # Same origin
        "http://127.0.0.1:4200",
        "http://127.0.0.1:8000",
    ],
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


# Health check endpoint
@app.get("/health")
async def health_check():
    """Server health check."""
    return {
        "status": "healthy",
        "service": "pmhelper",
        "version": "1.0.0"
    }


# Serve Angular static files (production only)
angular_dist = os.path.join(os.path.dirname(__file__), "../../../web/dist/pmhelper-edu-web")
if os.path.exists(angular_dist):
    app.mount("/", StaticFiles(directory=angular_dist, html=True), name="angular")
    logger.info(f"✅ Serving Angular app from {angular_dist}")
else:
    logger.info("ℹ️  Angular dist folder not found. Run in development mode.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "pmhelper.server.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Disable in production
        log_level="info"
    )
```

## Step 6: Docker Configuration

### 6.1 Dockerfile

**File**: `Dockerfile`

```dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml setup.py ./
COPY src/pmhelper/__init__.py src/pmhelper/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY src/ src/
COPY data/ data/

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "uvicorn", "pmhelper.server.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.2 Docker Compose

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
      - ./src:/app/src # For development hot-reload
    environment:
      - DATABASE_URL=sqlite:///data/pmhelper.db
      - DEBUG=false
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Step 7: Testing

### 7.1 Test Core Logic (No Server)

```python
# test_core.py
import asyncio
from pmhelper.core.calculator import Calculator, CalculationInput

async def test_calculator():
    calc = Calculator()
    input_data = CalculationInput(value=42, parameters={})
    result = await calc.calculate(input_data)
    print(f"Result: {result.result}")
    print(f"Time: {result.execution_time_ms}ms")

asyncio.run(test_calculator())
```

### 7.2 Test API Endpoint

```bash
# Using curl
curl -X POST http://localhost:8000/api/calculations/calculate \
  -H "Content-Type: application/json" \
  -d '{"value": 42, "parameters": {}}'
```

### 7.3 Test WebSocket

```javascript
// test_websocket.html
const ws = new WebSocket("ws://localhost:8000/ws/calculate");

ws.onopen = () => {
  console.log("Connected");
  ws.send(
    JSON.stringify({
      type: "calculate",
      data: { value: 42, parameters: {} },
    })
  );
};

ws.onmessage = (event) => {
  console.log("Result:", JSON.parse(event.data));
};
```

## Step 8: Run the Server

### Option 1: Direct Python

```powershell
# Install dependencies
pip install -e .

# Run server
python -m pmhelper.server.main

# Or with uvicorn
uvicorn pmhelper.server.main:app --reload
```

### Option 2: Docker

```powershell
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Step 9: Angular Integration

### 9.1 Install Dependencies

```bash
cd web
npm install
```

### 9.2 Create WebSocket Service

**File**: `web/src/app/services/calculation.service.ts`

```typescript
import { Injectable } from "@angular/core";
import { Observable, Subject } from "rxjs";

interface CalculationResult {
  type: string;
  success: boolean;
  data?: any;
  error?: string;
}

@Injectable({
  providedIn: "root",
})
export class CalculationService {
  private ws?: WebSocket;
  private messagesSubject = new Subject<CalculationResult>();

  connect(): void {
    this.ws = new WebSocket("ws://localhost:8000/ws/calculate");

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.messagesSubject.next(data);
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
  }

  sendCalculation(value: number, parameters: any = {}): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: "calculate",
          data: { value, parameters },
        })
      );
    }
  }

  getMessages(): Observable<CalculationResult> {
    return this.messagesSubject.asObservable();
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
    }
  }
}
```

## Deployment Checklist

### Development

- [x] Core logic separated from server
- [x] Database optimized for old laptop
- [x] API endpoints implemented
- [x] WebSocket handler implemented
- [x] Docker configuration created

### Before Production

- [ ] Add authentication
- [ ] Enable HTTPS
- [ ] Add rate limiting
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Add error tracking
- [ ] Performance testing
- [ ] Security audit

## Troubleshooting

### Database locked errors

```python
# Increase timeout in connection.py
connect_args={"timeout": 60}
```

### Slow performance on old laptop

```python
# Reduce concurrent connections
# In config.py
MAX_CONNECTIONS = 10
```

### WebSocket disconnections

```javascript
// Add reconnection logic in Angular
reconnect() {
  setTimeout(() => this.connect(), 1000);
}
```

## Next Steps

1. **Optimize database queries**: Add indexes as needed
2. **Add caching**: Use Redis for frequently accessed data
3. **Implement auth**: Add JWT authentication
4. **Monitor performance**: Set up logging and metrics
5. **Plan cloud migration**: When ready to scale

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Angular WebSocket](https://angular.io/guide/observables)
- [Docker Compose](https://docs.docker.com/compose/)
