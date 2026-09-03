# VIGILIS Local Setup Script

Write-Host "Starting VIGILIS Local Environment Setup..."

# Start Docker containers
Write-Host "Starting Docker containers (PostgreSQL, Redis)..."
docker-compose up -d

# Setup API Service
Write-Host "Setting up API Service..."
Set-Location -Path services\api
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install ..\..\packages\shared\
# Note: we need to make shared an installable package later, or just append to PYTHONPATH
Set-Location -Path ..\..

# Setup Ingestion Service
Write-Host "Setting up Ingestion Service..."
Set-Location -Path services\ingestion
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Set-Location -Path ..\..

# Setup AI Service
Write-Host "Setting up AI Service..."
Set-Location -Path services\ai
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Set-Location -Path ..\..

Write-Host "Setup complete!"
Write-Host "To run the services:"
Write-Host "API: cd services\api; .\venv\Scripts\Activate.ps1; python main.py"
Write-Host "Ingestion: cd services\ingestion; .\venv\Scripts\Activate.ps1; python main.py"
Write-Host "AI: cd services\ai; .\venv\Scripts\Activate.ps1; python main.py"
Write-Host "Web: cd apps\web; npm run dev"
