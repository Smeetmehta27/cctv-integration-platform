# VIGILIS: CCTV Sentinel Grid

A production-ready, highly scalable command center built for the **Gujarat Statewide CCTV Integration Hackathon**. VIGILIS fulfills the "Model 1: Centralised CCTV Registry & GIS Mapping" requirement while extending capabilities with real-time AI analytics (ANPR, Vehicle Tracking) and Watchlist Correlation.

## 🚀 Key Features
* **Statewide GIS Intelligence:** Keyless OpenStreetMap integration displaying scattered CCTV assets across Gujarat.
* **Robust AI Pipeline:** YOLOv8 + EasyOCR pipeline for real-time Automatic Number Plate Recognition (ANPR) and vehicle tracking.
* **Hackathon-Compliant Ingestion:** Strict adherence to video engineering guidelines (RTSP over TCP, PTS-based timing, exponential reconnect backoff, and graceful discontinuity handling).
* **Cloud Infrastructure:** Powered by a live Supabase PostgreSQL database utilizing an IPv4 transaction pooler and async connections.
* **Failsafe Operations:** Built-in `ENABLE_SIMULATION` mode to bypass venue network restrictions and guarantee a flawless demonstration.

## 🛠️ Architecture Stack
* **Frontend:** Next.js, React, Tailwind CSS, Leaflet (GIS)
* **Backend:** FastAPI, Python, Asyncio, HTTPX
* **AI Engine:** YOLOv8 (Tracking), EasyOCR (ANPR), OpenCV
* **Database:** Supabase (PostgreSQL + PostGIS)

## ⚙️ Running Locally
1. Set up your `.env` file with your Supabase `DATABASE_URL` (IPv4 pooler) and set `ENABLE_SIMULATION=true` (or `false` for live RTSP).
2. Start the FastAPI Backend: `python -m uvicorn services.api.main:app --host 0.0.0.0 --port 8000`
3. Start the AI Sentinel: `python -m services.ai.main`
4. Start the Frontend: `npm run dev` (from `apps/web`)
