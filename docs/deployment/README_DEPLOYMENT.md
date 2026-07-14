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

## Testing

### Run all tests

```powershell
pytest tests/ -v
```

### Run specific test file

```powershell
pytest tests/test_api.py -v
```

### Run with coverage

```powershell
pytest tests/ --cov=pmhelper --cov-report=html
```

## API Endpoints

### Health Check

```bash
GET /health
```

Returns server health status.

### Calculate

```bash
POST /api/calculations/calculate
Content-Type: application/json

{
  "value": 42,
  "parameters": {
    "multiplier": 2
  }
}
```

### WebSocket

```javascript
ws://localhost:8000/ws/calculate

// Send message
{
  "type": "calculate",
  "data": {
    "value": 42,
    "parameters": {}
  }
}

// Receive result
{
  "type": "result",
  "success": true,
  "data": {
    "result": 84,
    "execution_time_ms": 0.5,
    "metadata": {...}
  }
}
```

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

### Import Errors

If you see import errors, ensure the package is installed:

```powershell
pip install -e .
```

## Development Workflow

### 1. Create Feature Branch

```powershell
git checkout -b feat-new-feature
```

### 2. Make Changes

Edit files in `src/pmhelper/`

### 3. Test Locally

```powershell
# Run tests
pytest tests/ -v

# Start server
python -m pmhelper.server.main
```

### 4. Commit and Push

```powershell
git add .
git commit -m "feat: add new feature"
git push origin feat-new-feature
```

### 5. Merge to Production

```powershell
git checkout production
git merge feat-new-feature
git push origin production
```

## Database Management

### SQLite (Local)

Database file: `data/pmhelper.db`

```powershell
# View database
sqlite3 data/pmhelper.db
.tables
.schema
```

### PostgreSQL (Production)

Connect using Render.com dashboard or:

```bash
psql $DATABASE_URL
```

## Performance Tips

### For Old Laptop

- Keep `MAX_CONCURRENT_ANALYSES=3` or lower
- Use rate limiting (already configured)
- Monitor memory usage in task manager

### For Production

- Upgrade to Render.com paid tier ($7/month) for always-on
- Enable connection pooling (already configured)
- Monitor logs for slow queries

## Security

### Environment Variables

Never commit:

- `.env`
- `.env.local`
- `.env.production`

These are in `.gitignore`.

### API Keys

If you add API key authentication:

```python
# In config.py
API_KEY = os.getenv("API_KEY")
```

Set in Render.com dashboard.

## Important URLs (After Deployment)

- **Backend API**: https://pmhelper-api.onrender.com
- **API Docs** (dev only): https://pmhelper-api.onrender.com/api/docs
- **Health Check**: https://pmhelper-api.onrender.com/health
- **WebSocket**: wss://pmhelper-api.onrender.com/ws/calculate
- **Render Dashboard**: https://dashboard.render.com

## Support Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Async**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **Render Docs**: https://render.com/docs
- **PostgreSQL on Render**: https://render.com/docs/databases

## Cost Estimates

### Free Tier (First 90 Days)

- Backend: $0 (750 hours/month)
- Database: $0 (90 days)
- **Total: $0**

### After Free Tier

- Backend: $7/month (always-on)
- Database: $7/month (PostgreSQL)
- **Total: $14/month**

## Branch Strategy

- `main`: Development branch
- `production`: Stable releases (auto-deploys to Render.com)
- `feat-*`: Feature branches

## Validation Checklist

After deployment, verify:

- [ ] Server responds to `/health`
- [ ] API endpoint `/api/calculations/calculate` works
- [ ] WebSocket connects successfully
- [ ] Database is accessible
- [ ] CORS allows frontend connections
- [ ] Tests pass locally
- [ ] Logs show no errors

## Quick Commands Reference

```powershell
# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .

# Run server locally
python -m pmhelper.server.main

# Run tests
pytest tests/ -v

# Build Docker image
docker build -t pmhelper:latest .

# Run Docker container
docker-compose up

# Deploy to production
.\deploy_production.ps1
```

## Next Steps

1. **Implement actual PM calculations**: Replace the placeholder in `src/pmhelper/calculations.py` with your CPM/PERT/RCPS algorithms
2. **Add authentication**: Implement user authentication if needed
3. **Create frontend**: Build Angular app that connects to this API
4. **Add more tests**: Increase test coverage for production readiness
5. **Setup monitoring**: Add logging service (e.g., Sentry, LogRocket)

---

**Last Updated**: November 2025
**Version**: 1.0.0
**Maintainer**: PMHelper Team
