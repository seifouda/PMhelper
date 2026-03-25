# Deployment Options Without an Old Laptop

## Overview

If you don't have an old laptop available for self-hosting, there are several excellent **free and low-cost alternatives** that work perfectly for your 10-100 user MVP.

---

## Option 1: Use Your Current Development Machine (FREE)

### Best for: Development & Testing

**What**: Run the server on your current Windows laptop/desktop while developing.

**Pros**:

- ✅ Completely free
- ✅ Instant setup
- ✅ Easy to debug and test
- ✅ No additional hardware needed

**Cons**:

- ⚠️ Only available when your computer is on
- ⚠️ Not suitable for production
- ⚠️ Can't share with external users easily

**Setup**:

```powershell
# Just run locally
uvicorn pmhelper.server.main:app --reload

# Access at http://localhost:8000
```

**When to use**: Perfect for development and showing demos locally.

---

## Option 2: Railway.app (FREE → $5/month)

### Best for: Quick MVP deployment, easiest setup

**Free Tier**:

- 500 execution hours/month
- $5 credit/month
- Automatic deployments from GitHub
- Built-in PostgreSQL (free)
- HTTPS included

**Paid Tier**:

- $5/month for 500 hours + resources
- Pay-as-you-go after that
- No surprises

**Pros**:

- ✅ Easiest deployment (connect GitHub and done)
- ✅ Automatic HTTPS
- ✅ Free PostgreSQL database
- ✅ Great for startups
- ✅ Excellent developer experience

**Cons**:

- ⚠️ Can get expensive if you scale quickly
- ⚠️ Free tier sleeps after inactivity

**Setup**:

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Deploy
railway up

# 5. Add PostgreSQL (optional)
railway add --database postgres
```

**Configuration**:

```yaml
# railway.json
{
  "build": { "builder": "DOCKERFILE" },
  "deploy":
    {
      "startCommand": "uvicorn pmhelper.server.main:app --host 0.0.0.0 --port $PORT",
      "healthcheckPath": "/health",
    },
}
```

**Estimated Cost**:

- Months 1-2: **$0** (free tier)
- After scaling: **$5-10/month**

---

## Option 3: Render.com (FREE → $7/month)

### Best for: Production-ready free tier

**Free Tier**:

- 750 hours/month (more than Railway!)
- Free PostgreSQL database
- Automatic HTTPS
- Auto-sleep after 15 min inactivity
- Deploy from GitHub/GitLab

**Paid Tier**:

- $7/month for always-on
- Better performance
- No auto-sleep

**Pros**:

- ✅ Most generous free tier
- ✅ Production-ready infrastructure
- ✅ Free PostgreSQL (1GB)
- ✅ Easy to upgrade
- ✅ Great documentation

**Cons**:

- ⚠️ Free tier spins down after 15 min (cold starts ~30s)
- ⚠️ Slower than Railway for small apps

**Setup**:

1. Connect your GitHub repo
2. Select "Web Service"
3. Configure:
   - Build Command: `pip install -e .`
   - Start Command: `uvicorn pmhelper.server.main:app --host 0.0.0.0 --port $PORT`
4. Deploy!

**render.yaml** (Infrastructure as Code):

```yaml
services:
  - type: web
    name: pmhelper-api
    env: python
    buildCommand: pip install -e .
    startCommand: uvicorn pmhelper.server.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: pmhelper-db
          property: connectionString

databases:
  - name: pmhelper-db
    databaseName: pmhelper
    plan: free
```

**Estimated Cost**:

- Months 1-3: **$0** (free tier)
- When you need always-on: **$7/month**

---

## Option 4: Fly.io (FREE → $5/month)

### Best for: Global deployment, edge computing

**Free Tier**:

- 3 shared-cpu VMs (256MB RAM each)
- 3GB storage
- 160GB outbound data transfer
- Deploy globally

**Paid Tier**:

- $1.94/VM/month (scale as needed)
- Pay for what you use

**Pros**:

- ✅ Deploy close to users (global edge network)
- ✅ Generous free tier
- ✅ Excellent for distributed apps
- ✅ Great documentation
- ✅ Fast deployment

**Cons**:

- ⚠️ Small free tier VMs (256MB RAM)
- ⚠️ Requires PostgreSQL for persistence (SQLite ephemeral)
- ⚠️ Slightly more complex setup

**Setup**:

```bash
# 1. Install Fly CLI
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# 2. Login
fly auth login

# 3. Launch app
fly launch

# 4. Deploy
fly deploy

# 5. Add PostgreSQL (optional)
fly postgres create
```

**fly.toml**:

```toml
app = "pmhelper"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"

[[services]]
  http_checks = []
  internal_port = 8000
  processes = ["app"]
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

  [[services.http_checks]]
    interval = 10000
    grace_period = "5s"
    method = "get"
    path = "/health"
    protocol = "http"
    timeout = 2000
```

**Estimated Cost**:

- Months 1-6: **$0** (free tier sufficient)
- When scaling: **$5-10/month**

---

## Option 5: PythonAnywhere (FREE → $5/month)

### Best for: Python-specific hosting, simplest setup

**Free Tier**:

- 1 web app
- Python 3.x support
- 512MB storage
- HTTP only (no HTTPS on free)
- yourapp.pythonanywhere.com domain

**Paid Tier**:

- $5/month for basic HTTPS + custom domain
- More CPU time
- Better performance

**Pros**:

- ✅ Python-focused
- ✅ Very simple setup (no Docker needed)
- ✅ Great for learning
- ✅ Forever free tier

**Cons**:

- ⚠️ No HTTPS on free tier
- ⚠️ Limited to Python web apps
- ⚠️ CPU time limits on free tier
- ⚠️ Not as modern as Railway/Render

**Setup**:

1. Sign up at pythonanywhere.com
2. Go to "Web" tab
3. Add new web app (Flask/Django/Manual)
4. Upload your code
5. Configure WSGI file
6. Reload web app

**Estimated Cost**:

- MVP: **$0** (free tier)
- Production: **$5/month** (for HTTPS)

---

## Option 6: Heroku (FREE → $7/month)

### Status: Free tier discontinued, but still popular

**Note**: Heroku discontinued free tier in November 2022, but remains popular for paid hosting.

**Paid Tier**:

- $7/month for Eco Dynos
- Automatic scaling
- Add-ons marketplace
- Easy deployment

**Pros**:

- ✅ Very mature platform
- ✅ Huge ecosystem of add-ons
- ✅ Excellent documentation
- ✅ Git-based deployment

**Cons**:

- ❌ No free tier anymore
- ⚠️ More expensive than alternatives
- ⚠️ Dynos sleep on lower tiers

**Not recommended** due to lack of free tier and better alternatives available.

---

## Option 7: Oracle Cloud (Always Free Tier)

### Best for: Maximum free resources, willing to deal with complexity

**Always Free Tier**:

- 2 AMD VMs (1/8 OCPU, 1GB RAM each)
- 4 Arm VMs (4 cores, 24GB RAM total!)
- 200GB storage
- 10TB outbound data transfer/month
- **Forever free** (not a trial)

**Pros**:

- ✅ Most generous free tier ever
- ✅ Arm instances are very powerful
- ✅ Professional infrastructure
- ✅ Never expires

**Cons**:

- ⚠️ Complex setup (like AWS)
- ⚠️ Requires credit card
- ⚠️ Manual VM management
- ⚠️ Steeper learning curve

**Best for**: If you want maximum free resources and don't mind complexity.

---

## Option 8: Google Cloud Run (Pay-as-you-go)

### Best for: Serverless, automatic scaling

**Free Tier** (per month):

- 2 million requests
- 360,000 GB-seconds compute
- 180,000 vCPU-seconds

**Paid Tier**:

- Only pay when running
- $0.00002400 per GB-second
- Very cheap for low traffic

**Pros**:

- ✅ True serverless (only pay when used)
- ✅ Automatic scaling (0 → ∞)
- ✅ Google infrastructure
- ✅ Great for spiky traffic

**Cons**:

- ⚠️ Cold starts (~1-2s)
- ⚠️ More complex than Railway/Render
- ⚠️ Need to manage GCP

**Estimated Cost**:

- 10-100 users: **$0-2/month**
- 100-1000 users: **$5-15/month**

---

## Option 9: AWS Lightsail ($3.50/month)

### Best for: Cheap VPS with AWS reliability

**Pricing**:

- $3.50/month for 512MB RAM, 1 vCPU
- $5/month for 1GB RAM
- Predictable pricing

**Pros**:

- ✅ Cheapest AWS option
- ✅ Predictable pricing
- ✅ Full VM control
- ✅ AWS reliability

**Cons**:

- ⚠️ No free tier
- ⚠️ Manual setup required
- ⚠️ Need to manage security/updates

**Estimated Cost**: **$3.50-5/month**

---

## Option 10: Replit (FREE → $7/month)

### Best for: Quick prototypes, live collaboration

**Free Tier**:

- Public repls (code is public)
- Always-on projects (limited)
- Collaborative coding

**Paid Tier**:

- $7/month for private repls
- More compute resources
- Always-on

**Pros**:

- ✅ Zero setup (code in browser)
- ✅ Great for demos
- ✅ Live collaboration
- ✅ Built-in database

**Cons**:

- ⚠️ Not suitable for production
- ⚠️ Code is public on free tier
- ⚠️ Limited resources

**Best for**: Quick demos and learning, not production.

---

## Comparison Table

| Platform             | Free Tier   | Monthly Cost | Best For           | Difficulty  |
| -------------------- | ----------- | ------------ | ------------------ | ----------- |
| **Railway.app**      | 500 hrs     | $0 → $5      | Easiest deployment | ⭐ Easy     |
| **Render.com**       | 750 hrs     | $0 → $7      | Production ready   | ⭐ Easy     |
| **Fly.io**           | 3 VMs       | $0 → $5      | Global deployment  | ⭐⭐ Medium |
| **PythonAnywhere**   | Yes         | $0 → $5      | Python beginners   | ⭐ Easy     |
| **Oracle Cloud**     | 4 Arm VMs   | $0 forever   | Max free resources | ⭐⭐⭐ Hard |
| **Google Cloud Run** | 2M requests | $0 → $2      | Serverless         | ⭐⭐ Medium |
| **AWS Lightsail**    | No          | $3.50+       | AWS ecosystem      | ⭐⭐ Medium |
| **Replit**           | Public only | $0 → $7      | Quick demos        | ⭐ Easy     |

---

## Recommended Path for Your Use Case

### 🥇 **Recommended: Railway.app or Render.com**

**Why**:

- Easiest to set up (5 minutes)
- Free tier sufficient for MVP
- Automatic HTTPS
- GitHub integration
- PostgreSQL included
- Production-ready

**Which one**:

- **Railway** if you want simplest setup and don't mind potential future costs
- **Render** if you want more free hours and don't mind cold starts

### 🥈 **Alternative: Fly.io**

**Why**:

- Great free tier
- Global deployment
- Modern platform
- Good for learning DevOps

**Trade-off**: Slightly more complex setup

### 🥉 **Budget Option: Oracle Cloud**

**Why**:

- Most generous free tier (4 Arm cores!)
- Forever free
- Professional infrastructure

**Trade-off**: Complex setup, steep learning curve

---

## Step-by-Step: Deploy to Render.com (Recommended)

### 1. Prepare Your Repository

Ensure you have:

- `Dockerfile` in root
- `pyproject.toml` with dependencies
- `src/pmhelper/` with your code

### 2. Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Authorize Render to access your repos

### 3. Create Web Service

1. Click "New +" → "Web Service"
2. Select your PMhelper repository
3. Configure:
   - **Name**: `pmhelper-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -e .`
   - **Start Command**: `uvicorn pmhelper.server.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

### 4. Add PostgreSQL (Optional)

1. Click "New +" → "PostgreSQL"
2. Name: `pmhelper-db`
3. Plan: Free
4. Create database

### 5. Connect Database to Service

1. Go to your web service
2. Environment tab
3. Add environment variable:
   - Key: `DATABASE_URL`
   - Value: Select "From Database" → pmhelper-db

### 6. Deploy!

1. Click "Create Web Service"
2. Wait for build (~2-3 minutes)
3. Your app is live at `https://pmhelper-api.onrender.com`

### 7. Test

```bash
# Health check
curl https://pmhelper-api.onrender.com/health

# Test calculation
curl -X POST https://pmhelper-api.onrender.com/api/calculations/calculate \
  -H "Content-Type: application/json" \
  -d '{"value": 42, "parameters": {}}'
```

---

## Cost Comparison Over Time

### MVP Phase (0-100 users, 3 months)

| Platform      | Month 1 | Month 2 | Month 3 | Total      |
| ------------- | ------- | ------- | ------- | ---------- |
| Railway       | $0      | $0      | $0      | **$0**     |
| Render        | $0      | $0      | $0      | **$0**     |
| Fly.io        | $0      | $0      | $0      | **$0**     |
| Oracle Cloud  | $0      | $0      | $0      | **$0**     |
| AWS Lightsail | $3.50   | $3.50   | $3.50   | **$10.50** |

### Growth Phase (100-500 users, 6 months)

| Platform      | Monthly Cost | 6 Month Total |
| ------------- | ------------ | ------------- |
| Railway       | $5-10        | **$30-60**    |
| Render        | $7           | **$42**       |
| Fly.io        | $5-8         | **$30-48**    |
| Oracle Cloud  | $0           | **$0**        |
| AWS Lightsail | $5           | **$30**       |

---

## My Recommendation

### For Your Specific Case:

**Start with Render.com FREE tier**

**Reasons**:

1. ✅ **750 hours/month** - More than enough for MVP
2. ✅ **Free PostgreSQL** - Better than SQLite for production
3. ✅ **Automatic HTTPS** - Secure by default
4. ✅ **5 minute setup** - No DevOps needed
5. ✅ **GitHub integration** - Auto-deploy on push
6. ✅ **$0 for 3+ months** - Perfect for validation
7. ✅ **Easy upgrade** - $7/month when ready

**Timeline**:

- **Week 1**: Deploy to Render.com free tier
- **Months 1-3**: Validate with users on free tier
- **Month 4+**: Upgrade to $7/month if validated

**Total cost for first 6 months**: **$0-21**

---

## Quick Start Command

```bash
# Deploy to Render.com in 5 minutes
# 1. Sign up at render.com with GitHub
# 2. Connect your PMhelper repo
# 3. Click "New Web Service"
# 4. Use these settings:

Build Command: pip install -e .
Start Command: uvicorn pmhelper.server.main:app --host 0.0.0.0 --port $PORT

# Done! Your app is live at https://your-app.onrender.com
```

---

## Summary

**Don't have an old laptop? No problem!**

You have **multiple free options** that are actually **better** than self-hosting:

- ✅ Always available (not dependent on your laptop being on)
- ✅ Automatic HTTPS
- ✅ Professional infrastructure
- ✅ Easy to scale
- ✅ No hardware maintenance

**Best choice**: **Render.com** free tier → upgrade to $7/month when validated.

**Budget**: $0 for MVP, $7/month when scaling, $50-100/month at 1000+ users.

---

_Last Updated: October 28, 2025_
