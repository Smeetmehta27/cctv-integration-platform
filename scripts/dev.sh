#!/bin/bash
# VIGILIS One-Click Local Development Launcher for Linux/macOS

echo -e "\033[0;36m========================================\033[0m"
echo -e "\033[0;36mVIGILIS: Local Development Launcher\033[0m"
echo -e "\033[0;36m========================================\033[0m"

# 1. Prerequisite Checks
echo -e "\033[0;33m[1/4] Checking prerequisites...\033[0m"
if ! command -v docker &> /dev/null; then
    echo -e "\033[0;31mDocker is not installed or not in PATH.\033[0m"
    exit 1
fi
if ! command -v python3 &> /dev/null; then
    echo -e "\033[0;31mPython3 is not installed or not in PATH.\033[0m"
    exit 1
fi
if ! command -v npm &> /dev/null; then
    echo -e "\033[0;31mNode.js (npm) is not installed or not in PATH.\033[0m"
    exit 1
fi

# 2. Start Docker Services
echo -e "\033[0;33m[2/4] Starting Docker services (PostgreSQL & Redis)...\033[0m"
docker-compose up -d

echo -e "\033[0;33mWaiting for database to accept connections...\033[0m"
sleep 5

# 3. Start Backend API
echo -e "\033[0;33m[3/4] Starting FastAPI Backend on port 8000...\033[0m"
python3 -m uvicorn services.api.main:app --port 8000 --reload &
API_PID=$!

sleep 3

# 4. Start Next.js Frontend
echo -e "\033[0;33m[4/4] Starting Next.js Frontend on port 3000...\033[0m"
cd apps/web || exit
npm run dev &
FRONTEND_PID=$!
cd ../.. || exit

echo -e ""
echo -e "\033[0;32m========================================\033[0m"
echo -e "\033[0;32mSYSTEM IS ONLINE AND RUNNING\033[0m"
echo -e "\033[0;32m========================================\033[0m"
echo -e "\033[1;37m-> Frontend UI: http://localhost:3000\033[0m"
echo -e "\033[1;37m-> Backend API: http://localhost:8000/docs\033[0m"
echo -e ""
echo -e "\033[0;33mTo run the automated E2E smoke tests, execute:\033[0m"
echo -e "\033[0;36m  python3 scripts/test_e2e.py\033[0m"
echo -e "\033[0;32m========================================\033[0m"

# Handle graceful shutdown
trap "kill $API_PID $FRONTEND_PID; docker-compose stop; exit" SIGINT SIGTERM
wait
