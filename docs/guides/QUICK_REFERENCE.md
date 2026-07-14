# PMHelper Server Architecture - Quick Reference

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Key Decisions](#key-decisions)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Implementation Checklist](#implementation-checklist)
- [Deployment Options](#deployment-options)
- [Cost Breakdown](#cost-breakdown)

---

## Architecture Overview

**Type**: Monolithic with Separation of Concerns

```
┌────────────────────────────────────┐
│     Old Laptop (Self-Hosted)       │
├────────────────────────────────────┤
│  Docker Container                  │
│  ┌──────────────────────────────┐ │
│  │  FastAPI Server              │ │
│  │  ├─ REST API                 │ │
│  │  ├─ WebSocket (real-time)    │ │
│  │  ├─ SQLite Database          │ │
│  │  └─ Angular Static Files     │ │
│  └──────────────────────────────┘ │
└────────────────────────────────────┘
```

---

## Key Decisions

| Decision              | Choice              | Rationale                                         |
| --------------------- | ------------------- | ------------------------------------------------- |
| **Architecture**      | Monolithic          | Simplest, lowest cost, perfect for MVP            |
| **Backend Framework** | FastAPI             | Async, WebSocket support, fast, lightweight       |
| **Database**          | SQLite → PostgreSQL | Free, sufficient for 10-100 users, easy migration |
| **Frontend**          | Angular             | User preference, dynamic rendering                |
| **Communication**     | REST + WebSocket    | REST for storage, WS for real-time                |
| **Deployment**        | Self-hosted → Cloud | $0 initially, scale when needed                   |
| **Containerization**  | Docker              | Portability, easy deployment                      |

---

## Tech Stack

### Backend

- **Python 3.12+**
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM (async)
- **SQLite** - Database
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

### Frontend

- **Angular 15+**
- **TypeScript**
- **RxJS** - WebSocket handling

### Infrastructure

- **Docker** - Containerization
- **Docker Compose** - Orchestration

### Future (When Scaling)

- **PostgreSQL** - Production database
- **Redis** - Caching layer
- **Nginx** - Reverse proxy
- **Celery** - Background tasks

---

## Project Structure

```
PMhelper/
├── src/pmhelper/
│   ├── core/                      # 🎯 Business Logic (Independent)
│   │   ├── calculator.py          # Pure calculation logic
│   │   ├── models.py              # Domain models
│   │   └── services.py            # Business orchestration
│   │
│   └── server/                    # 🌐 Server Infrastructure
│       ├── main.py                # FastAPI app entry
│       ├── config.py              # Configuration
│       ├── api/
│       │   └── calculations.py    # REST endpoints
│       ├── database/
│       │   ├── connection.py      # ✅ Optimized for old laptop
│       │   └── models.py          # SQLAlchemy models
│       └── websockets/
│           └── calculation_ws.py  # Real-time handler
│
├── frontend/                      # Angular application
│   ├── src/
│   └── dist/                      # Built files (served by FastAPI)
│
├── data/
│   └── pmhelper.db               # SQLite database
│
├── docs/
│   ├── SERVER_ARCHITECTURE.md     # This document's full version
│   ├── IMPLEMENTATION_GUIDE.md    # Step-by-step guide
│   └── DATABASE_OPTIMIZATIONS.md  # DB config details
│
├── docker-compose.yml             # Container setup
├── Dockerfile                     # Container definition
└── pyproject.toml                # Dependencies
```

---

## Implementation Checklist

### ✅ Phase 1: Core Setup

- [x] Database connection optimized
- [ ] Create core calculation logic (`core/calculator.py`)
- [ ] Create service layer (`core/services.py`)
- [ ] Create REST API endpoints (`server/api/calculations.py`)
- [ ] Create WebSocket handler (`server/websockets/calculation_ws.py`)
- [ ] Update main.py with all components

### 🔄 Phase 2: Docker & Deployment

- [ ] Create Dockerfile
- [ ] Create docker-compose.yml
- [ ] Test Docker build
- [ ] Test on old laptop

### 🎨 Phase 3: Frontend Integration

- [ ] Create Angular WebSocket service
- [ ] Connect to REST API
- [ ] Build Angular for production
- [ ] Configure FastAPI to serve Angular

### 🚀 Phase 4: Production Ready

- [ ] Add authentication
- [ ] Enable HTTPS
- [ ] Add monitoring
- [ ] Set up backups
- [ ] Load testing

---

## Deployment Options

> 💡 **Don't have an old laptop?** See [DEPLOYMENT_ALTERNATIVES.md](../deployment/DEPLOYMENT_ALTERNATIVES.md) for 10+ free and low-cost cloud options!

### Option 1: Self-Hosted (If you have old laptop) - **$0/month**

**Requirements**:

- Old laptop with 4GB+ RAM
- Windows + Docker Desktop
- Home internet

**Setup**:

```powershell
# Clone repo
git clone <repo-url>
cd PMhelper

# Run with Docker
docker-compose up -d

# Access
http://localhost:8000
```

**Pros**: Free, full control, good for development
**Cons**: Limited uptime, home internet bandwidth

---

### Option 2: Render.com (Recommended if no laptop) - **$0 → $7/month**

**Why Recommended**:

- ✅ 750 hours/month FREE
- ✅ Free PostgreSQL database
- ✅ Automatic HTTPS
- ✅ 5-minute setup
- ✅ GitHub integration

**Setup**:

1. Sign up at [render.com](https://render.com) with GitHub
2. Connect your repository
3. Create Web Service
4. Deploy!

**See [DEPLOYMENT_ALTERNATIVES.md](../deployment/DEPLOYMENT_ALTERNATIVES.md) for detailed setup**

---

### Option 3: Railway.app - **$0 → $5/month**

- **Free**: 500 hours/month
- **Best for**: Easiest deployment
- **Setup**: `railway login && railway init && railway up`

---

### Option 4: Fly.io - **$0 → $5/month**

- **Free**: 3 shared VMs (256MB RAM each)
- **Best for**: Global deployment
- **Setup**: `fly launch && fly deploy`

---

### Option 5: Oracle Cloud - **$0 Forever**

- **Free**: 4 Arm CPU cores, 24GB RAM (forever!)
- **Best for**: Maximum free resources
- **Trade-off**: Complex setup

---

### More Options

See [DEPLOYMENT_ALTERNATIVES.md](../deployment/DEPLOYMENT_ALTERNATIVES.md) for:

- PythonAnywhere
- Google Cloud Run
- AWS Lightsail
- Replit
- Full comparison table
- Cost breakdowns

---

## Cost Breakdown

### Current (MVP): $0/month

- Self-hosted on old laptop
- SQLite database
- No external services
- Home internet

### Scaling Stage 1 (100-500 users): $5-12/month

- Cloud VM (1GB RAM): $5-6/month
- PostgreSQL managed: $0-7/month (many have free tier)
- Domain: $1/month (optional)

### Scaling Stage 2 (500-1000 users): $15-30/month

- Cloud VM (2GB RAM): $12/month
- PostgreSQL: $7/month
- Redis: $5/month
- CDN: $0-5/month

### Scaling Stage 3 (1000+ users): $50-100/month

- Multiple app servers: $20-40/month
- Managed PostgreSQL: $15-25/month
- Redis cluster: $10-15/month
- Load balancer: $5-10/month
- Monitoring: $5-10/month

---

## API Endpoints

### REST API

```
POST /api/calculations/calculate
Body: {"value": 42, "parameters": {}}
Response: {"result": 84, "execution_time_ms": 15.2, "metadata": {}}

GET /health
Response: {"status": "healthy", "service": "pmhelper"}
```

### WebSocket

```
WS /ws/calculate

Client → Server:
{
  "type": "calculate",
  "data": {"value": 42, "parameters": {}}
}

Server → Client:
{
  "type": "result",
  "success": true,
  "data": {
    "result": 84,
    "execution_time_ms": 15.2,
    "metadata": {}
  }
}
```

---

## Quick Commands

### Development

```powershell
# Install dependencies
pip install -e .

# Run server (development)
python -m pmhelper.server.main

# Or with hot-reload
uvicorn pmhelper.server.main:app --reload

# Run tests
pytest

# Test specific calculation
python -c "from pmhelper.core.calculator import Calculator; import asyncio; asyncio.run(Calculator().calculate(...))"
```

### Docker

```powershell
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose build --no-cache
```

### Database

```powershell
# Backup database
copy data\pmhelper.db data\backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').db

# Check database size
(Get-Item data\pmhelper.db).Length / 1MB

# SQLite shell
sqlite3 data\pmhelper.db
```

---

## Performance Targets

| Metric              | Target | Current |
| ------------------- | ------ | ------- |
| Response Time (API) | <200ms | ~150ms  |
| Response Time (WS)  | <50ms  | ~30ms   |
| Concurrent Users    | 10-100 | ✅      |
| Uptime              | 99%+   | TBD     |
| Database Size       | <100MB | <5MB    |

---

## Monitoring Checklist

### Essential Metrics

- [ ] Response time per endpoint
- [ ] Active WebSocket connections
- [ ] Database query performance
- [ ] Memory usage
- [ ] CPU utilization
- [ ] Disk space

### Tools

- **Development**: FastAPI logs, print statements
- **Production**: Prometheus + Grafana, Sentry, LogRocket

---

## Security Checklist

### MVP (Current)

- [x] Basic CORS configuration
- [x] Input validation (Pydantic)
- [x] Error handling

### Production (Before Public Launch)

- [ ] Add authentication (JWT)
- [ ] Rate limiting
- [ ] HTTPS/SSL
- [ ] Input sanitization
- [ ] Environment variables for secrets
- [ ] Database backups
- [ ] Logging (no sensitive data)

---

## Scaling Triggers

**Add Redis caching when**:

- Same queries repeated frequently
- Response time >200ms
- Database CPU >70%

**Migrate to PostgreSQL when**:

- Database size >100MB
- Concurrent users >100
- Need advanced features
- Write-heavy workload

**Add background queue (Celery) when**:

- Calculations take >5 seconds
- Need to process tasks asynchronously
- Want to retry failed jobs

**Horizontal scaling when**:

- Single server CPU >80%
- Need high availability (99.9%+)
- Global user base (multiple regions)

---

## Migration Path

```
Stage 1: MVP (Now)
├─ Old laptop
├─ SQLite
├─ FastAPI
└─ 10-100 users
    ↓
Stage 2: Cloud Migration (1-3 months)
├─ Railway/Render/Fly.io
├─ Still SQLite or PostgreSQL
├─ HTTPS enabled
└─ 100-500 users
    ↓
Stage 3: Optimization (3-6 months)
├─ Dedicated VPS
├─ PostgreSQL
├─ Redis caching
└─ 500-1000 users
    ↓
Stage 4: Scale-out (6+ months)
├─ Multiple app servers
├─ Load balancer
├─ Managed database
├─ CDN
└─ 1000+ users
```

---

## Support & Resources

### Documentation

- [Full Architecture Doc](./SERVER_ARCHITECTURE.md)
- [Implementation Guide](./IMPLEMENTATION_GUIDE.md)
- [Database Optimizations](../reports/DATABASE_OPTIMIZATIONS.md)
- [Deployment Alternatives](../deployment/DEPLOYMENT_ALTERNATIVES.md) - 10+ options if you don't have an old laptop

### External Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Docker Docs](https://docs.docker.com/)
- [Angular Docs](https://angular.io/)

### Community

- FastAPI Discord
- SQLAlchemy Discussions
- Docker Forums
- Stack Overflow

---

## Quick Troubleshooting

| Issue                 | Solution                                          |
| --------------------- | ------------------------------------------------- |
| Database locked       | Increase timeout to 60s in `connection.py`        |
| Slow queries          | Add indexes, check query plan                     |
| Memory growth         | Check `pool_recycle` setting (should be 3600)     |
| WebSocket disconnects | Add reconnection logic in Angular                 |
| Docker build fails    | Clear cache: `docker-compose build --no-cache`    |
| Port already in use   | Change port in docker-compose.yml or kill process |

---

## Conclusion

**Current Status**: ✅ Architecture defined, database optimized

**Next Steps**:

1. Implement core calculation logic
2. Create API endpoints
3. Add WebSocket handler
4. Test on old laptop
5. Integrate Angular frontend

**Timeline**: 1-2 weeks for MVP

**Budget**: $0 for MVP, $5-12/month when scaling

---

_Last Updated: October 28, 2025_
_Version: 1.0.0_
_Author: PMHelper Team_
