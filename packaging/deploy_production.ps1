# Production deployment script for PMHelper (Windows)
$ErrorActionPreference = "Stop"

# This script lives in packaging\. Operate from the repo root.
Set-Location (Split-Path $PSScriptRoot -Parent)

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
