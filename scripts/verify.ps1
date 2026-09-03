# VIGILIS Phase 2 Verification Script

Write-Host "=========================================="
Write-Host "VIGILIS FOUNDATION VERIFICATION"
Write-Host "=========================================="

# 1. Check Python syntax in API
Write-Host "`n[1] Checking Python Syntax..."
Set-Location -Path c:\Gujarat-Hackathon\services\api
python -m py_compile main.py
if ($?) {
    Write-Host "PASS: Python syntax is valid." -ForegroundColor Green
} else {
    Write-Host "FAIL: Python syntax errors found." -ForegroundColor Red
}
Set-Location -Path c:\Gujarat-Hackathon

# 2. Check Database / Docker Availability
Write-Host "`n[2] Checking Docker & Database..."
docker --version > $null 2>&1
if ($?) {
    Write-Host "PASS: Docker is available." -ForegroundColor Green
} else {
    Write-Host "BLOCKED: Docker is unavailable. API will use local fallback mode." -ForegroundColor Yellow
}

# 3. Check Frontend Build
Write-Host "`n[3] Checking Frontend Build Configuration..."
Set-Location -Path c:\Gujarat-Hackathon\apps\web
npm run build
if ($?) {
    Write-Host "PASS: Next.js frontend built successfully." -ForegroundColor Green
} else {
    Write-Host "FAIL: Next.js frontend build failed." -ForegroundColor Red
}
Set-Location -Path c:\Gujarat-Hackathon

Write-Host "`n=========================================="
Write-Host "VERIFICATION COMPLETE"
Write-Host "=========================================="
