# CCTV Integration Platform (VIGILIS Prototype)

## Overview
VIGILIS is a modular, secure, and scalable CCTV video-intelligence platform designed to solve the problem of fragmented surveillance systems. It integrates heterogeneous departmental CCTV systems, VMS platforms, RTSP streams, and future feeds into a unified video intelligence platform for enhanced situational awareness.

## Hackathon Context
This platform is designed specifically for heterogeneous departmental CCTV/VMS integration. Existing departmental VMS infrastructure remains operational while this platform provides a common integration, intelligence, analytics, and command-center layer.

## Version 2.0 Checkpoint (Production Architecture)
- **Offline-First Resilience:** Synchronous local SQLite edge-database auto-provisioning if cloud DNS fails.
- **Zero-500 Architecture:** Cascading database try/except fallbacks ensuring the API and Next.js GIS map never crash during schema mismatches.
- **Automated Validation:** Fully passing E2E Python test suite for camera registry, websockets, and AI telemetry.

## Architecture
Our hybrid architecture combines the following core concepts:
- **Central CCTV Registry + GIS**: A unified geospatial registry of all camera assets.
- **Unified Viewing + Metadata Analytics**: A single pane of glass for live streams and AI-generated metadata.
- **VMS Federation + Middleware**: Connects disparate department VMS systems without replacing them.
- **Selected centralized capabilities**: AI analytics run centrally where appropriate to provide intelligence without overburdening edge devices.

## Current Features
- **Frontend Dashboard**: Interactive Next.js web application with a GIS map for camera tracking.
- **API Gateway**: FastAPI backend for client communication, camera management, and websocket alerts.
- **AI Analytics**: PyTorch/OpenCV-based service for processing video streams.
- **Ingestion Service**: Handles RTSP streams.
- **Database**: PostgreSQL integration for persistent storage of camera metadata and alerts.

## Technology Stack
- **Frontend**: Next.js, React, Tailwind CSS, MapLibre GL JS
- **Backend Services**: Python, FastAPI, WebSockets
- **Database/Cache**: PostgreSQL, Redis
- **AI/CV**: PyTorch, OpenCV, EasyOCR

## Architecture Flow
```text
Departmental CCTV / VMS
        ↓
Integration / Federation Layer
        ↓
Stream Gateway
        ↓
AI / Video Analytics
        ↓
Metadata
        ↓
Watchlist Matching
        ↓
Alert Engine
        ↓
Police Intelligence Dashboard
```

## Running Locally

### 1. Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- PostgreSQL (or fallback mode)
- Redis

### 2. Environment Variables
Create a `.env` file based on the provided `.env.example`.
```powershell
Copy-Item .env.example .env
```
Ensure all required variables such as `DB_HOST`, `DB_PASSWORD`, and API host configurations are correctly set. Never commit the actual `.env` file containing real credentials to version control.

### 3. Setup Dependencies
```powershell
.\scripts\setup.ps1
```

### 4. Running the Application

**Frontend:**
```powershell
cd apps\web
npm install
npm run dev
```

**Backend (API):**
```powershell
cd services\api
.\venv\Scripts\Activate.ps1
python main.py
```
*(Repeat the backend process for `services\ai` and `services\ingestion` if running fully locally)*

### 5. Verification
Run the verification script to ensure services are correctly configured:
```powershell
.\scripts\verify.ps1
```

## Project Structure
- `apps/web/`: Next.js frontend application and dashboard.
- `services/api/`: FastAPI central communication and REST API.
- `services/ai/`: Python-based AI analytics microservice.
- `services/ingestion/`: RTSP stream ingestion microservice.
- `packages/shared/`: Shared Python packages and utilities.
- `scripts/`: PowerShell scripts for local development setup and verification.

## Hackathon Demo
The current end-to-end workflow demonstrates:
1. Initiating the local backend services and Next.js frontend.
2. Viewing the unified interface via the Next.js web dashboard.
3. Accessing the central CCTV registry on the MapLibre GIS map.
