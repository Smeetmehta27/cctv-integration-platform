<#
.SYNOPSIS
VIGILIS One-Click Local Development Launcher for Windows (PowerShell)

.DESCRIPTION
This script verifies dependencies, starts Docker services, initiates the Python API backend,
and launches the Next.js frontend for immediate local development.
#>

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VIGILIS: Local Development Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Prerequisite Checks
Write-Host "[1/4] Checking prerequisites..." -ForegroundColor Yellow
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker is not installed or not in PATH." -ForegroundColor Red
    exit 1
}
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not installed or not in PATH." -ForegroundColor Red
    exit 1
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js (npm) is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

# 2. Start Docker Services
Write-Host "[2/4] Starting Docker services (PostgreSQL & Redis)..." -ForegroundColor Yellow
docker-compose up -d

# Wait for DB to be healthy
Write-Host "Waiting for database to accept connections..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 3. Start Backend API
Write-Host "[3/4] Starting FastAPI Backend on port 8000..." -ForegroundColor Yellow
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m uvicorn services.api.main:app --port 8000 --reload"

# Wait for API
Start-Sleep -Seconds 3

# 4. Start Next.js Frontend
Write-Host "[4/4] Starting Next.js Frontend on port 3000..." -ForegroundColor Yellow
Set-Location -Path "apps/web"
Start-Process -NoNewWindow -FilePath "npm" -ArgumentList "run dev"
Set-Location -Path "../.."

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "SYSTEM IS ONLINE AND RUNNING" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "-> Frontend UI: http://localhost:3000" -ForegroundColor White
Write-Host "-> Backend API: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "To run the automated E2E smoke tests, execute:" -ForegroundColor Yellow
Write-Host "  python scripts/test_e2e.py" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green
