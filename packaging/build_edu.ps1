# PMhelper Edu — Build Script
# Usage: .\build_edu.ps1
# Produces: dist\PMhelper_Edu\ (onedir bundle)

Write-Host "=== PMhelper Edu Build ===" -ForegroundColor Cyan

# This script lives in packaging\. Run from the repo root so the spec's src\/assets\
# paths resolve.
Set-Location (Split-Path $PSScriptRoot -Parent)

# Check PyInstaller
$pyinstaller = Get-Command pyinstaller -ErrorAction SilentlyContinue
if (-not $pyinstaller) {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Clean previous build
if (Test-Path "build\PMhelper_Edu") {
    Remove-Item -Recurse -Force "build\PMhelper_Edu"
}
if (Test-Path "dist\PMhelper_Edu") {
    Remove-Item -Recurse -Force "dist\PMhelper_Edu"
}

# Build
Write-Host "Building..." -ForegroundColor Green
pyinstaller (Join-Path $PSScriptRoot 'pmhelper_edu.spec') --noconfirm

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nBuild successful!" -ForegroundColor Green
    Write-Host "Output: dist\PMhelper_Edu\" -ForegroundColor Cyan
    Write-Host "Run:    dist\PMhelper_Edu\PMhelper_Edu.exe" -ForegroundColor Cyan
} else {
    Write-Host "`nBuild failed!" -ForegroundColor Red
    exit 1
}
