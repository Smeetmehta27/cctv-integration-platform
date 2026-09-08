# VIGILIS: Statewide CCTV Sentinel Grid & AI Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg)](https://www.postgresql.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF.svg)](https://ultralytics.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Gujarat Statewide CCTV Integration Hackathon**  
> **Submission Model:** Hybrid / Innovative Architecture (Built on Mandatory Model 1 Foundation)  
> **Core Objective:** Unify fragmented departmental CCTV ecosystems, enable edge-to-cloud automated video analytics (ANPR & Tracking), and provide real-time watchlist correlation ready to scale to ~80,000 cameras across Gujarat.

---

## Evaluation Framework Alignment

### 01. Successful Test Case
**Implementation:** The platform onboards government-provided feeds (or heterogeneous sources) via the RTSP/ONVIF path using `services/ai/ingest_worker.py` (forced TCP transport, PTS-driven framing). For environments blocking RTSP, a recorded viewing fallback is fully functional via the `ENABLE_SIMULATION=true` mode, which pipes the `demo_traffic.mp4` video through the same real AI pipeline. Analytics output is emitted as lightweight JSON telemetry over WebSockets to the frontend.

### 02. Solution Presentation
**Implementation:** This README serves as the primary technical entry point. The formal presentation deck (PPT/PDF) is not currently committed to the repository. Please request the official presentation file for the high-level business pitch.

### 03. Solution Architecture
**Implementation:** The system follows a **Hybrid Federation Model** detailed in [`docs/HIGH_LEVEL_DESIGN.md`](./docs/HIGH_LEVEL_DESIGN.md). 
- **Model 1 (Registry Federation):** Existing IP cameras are registered in the central PostGIS database.
- **Model 2 (Stream Gateway Federation):** Legacy feeds are proxied regionally.
- **Model 3 (AI Metadata Federation):** Edge nodes perform heavy inference locally and transmit only lightweight JSON.
*(See the System Architecture diagram below for the full data flow).*

### 04. Working Platform and Demonstration
**Implementation:** The full-stack platform (FastAPI, Next.js, YOLOv8) runs seamlessly against both live RTSP feeds and simulation video. Code health is verified with 6/6 automated end-to-end integration tests:
- `[PASS] [TEST 1] Camera Registry - Found 30 cameras in registry`
- `[PASS] [TEST 2] Health Telemetry - Health telemetry verified (Real health endpoint reachable)`
- `[PASS] [TEST 3] Plate Normalization - Canonical resolution to GJ01ER8842 verified`
- `[PASS] [TEST 4] Route Reconstruction - Reconstructed route with 0 nodes`
- `[PASS] [TEST 5] Report Generation - CSV and PDF report generations succeeded`
- `[PASS] [TEST 6] Video Stream Availability - MJPEG boundary bytes verified`

### 05. Video Analytics Output
**Implementation:** The edge AI pipeline utilizes a custom YOLOv8 model (`services/ai/itd_yolov8.pt`) to detect 8 vehicle/object classes: `two wheeler`, `autorickshaw`, `car`, `bus`, `LCV`, `truck`, `bicycle`, and `pedestrain`. EasyOCR performs ANPR with output stabilized by the `IndianPlateNormalizer`. Tracks generate millisecond-accurate timestamps. The system natively supports cross-camera route reconstruction and generates CSV/PDF export reports (verified in Test 5).

### 06. Scalability and PoC Readiness
**Implementation:** As calculated in [`docs/SCALE_PLAN_80K.md`](./docs/SCALE_PLAN_80K.md), transmitting 80,000 raw 1080p streams centrally would require an impossible ~320 Gbps. Our Metadata-First architecture reduces central WAN usage to ~1.6 Gbps. The compute tier scales via ~1,000 NVIDIA L4 GPUs distributed across 6 regional clusters (~166 per region). The data layer utilizes 3 storage tiers (10TB Hot, 50TB Warm, 1PB Cold) and targets an RPO < 5s and RTO < 60s for High Availability.

### 07. Submission Completeness
- [x] Full Source Code (Edge AI, Central API, Web Dashboard)
- [x] High-Level Design (`docs/HIGH_LEVEL_DESIGN.md`)
- [x] Scale Plan (`docs/SCALE_PLAN_80K.md`)
- [x] Demo Script (`docs/EVALUATION_DEMO_SCRIPT.md`)
- [x] End-to-End Test Suite (`scripts/test_e2e.py`)
- [x] Trained Model Weights & Video (`itd_yolov8.pt`, `demo_traffic.mp4` via Git LFS)
- [x] Database Schema & Seed Data (`database/`)
- [x] MIT License

---

## Bonus Capabilities

**Innovative hybrid or customised architecture with clear operational value:**
*(Fully Implemented)* Demonstrated in `services/ai/ingest_worker.py` and `services/ai/tracker_manager.py`. The edge node handles heavy video decoding and object tracking, ensuring only ~16kb JSON payloads traverse the central WAN, cutting bandwidth by >99%.

**Advanced cross-camera vehicle movement tracking or multi-camera correlation:**
*(Fully Implemented)* Demonstrated in `services/ai/tracker_manager.py` (`RouteReconstructor` class). The backend computes haversine distances, time deltas, and validates physical transit speeds between camera nodes to reconstruct vehicle trajectories.

**Additional reliable analytics beyond the mandatory ANPR requirement:**
*(Fully Implemented)* The YOLOv8 pipeline actively classifies 8 distinct vehicle/object types. Additionally, `services/ai/plate_normalizer.py` provides heuristic plate syntax stabilization, correcting state-code transliteration errors (e.g. 0 vs O).

**Strong edge-processing, bandwidth-optimisation, or low-connectivity operation:**
*(Fully Implemented)* The ingestion adapter (`ingest_worker.py`) forces RTSP over TCP, utilizes PTS pacing instead of brittle FPS timing, and implements an exponential reconnect backoff to prevent tight-loop crashes in unstable network environments.

**Enhanced cybersecurity, privacy protection, auditability, or role-based access controls:**
*(Designed Only)* The architecture in `docs/HIGH_LEVEL_DESIGN.md` mandates GSWAN MPLS isolation, mTLS for node authentication, and AES-256 for data at rest. Role-Based Access Control (RBAC) is planned but **not implemented** in the current PoC code (e.g., `services/api/main.py` currently operates without strict auth middleware).

**Operational dashboards, automated alerts, health monitoring, or integration-ready APIs:**
*(Partially Implemented)* Live WebSocket alerts and the Next.js GIS dashboard are fully implemented. Camera registry and health APIs exist (`services/api/routes/health.py`). Deeper automated health monitoring and load balancing are aspirational roadmap features.

---

## Infrastructure & Operations Detail

- **Central, Regional, and Edge-Compute Requirements:**
  The topology spans three tiers:
  - **Edge Nodes:** Field deployments at camera sites handling raw video ingestion and localized YOLO inference.
  - **6 Regional GPU Clusters:** Located in Ahmedabad, Surat, Vadodara, Rajkot, Bhavnagar, and Gandhinagar. These handle heavy metadata extraction and caching for legacy IP cameras lacking edge compute.
  - **Central Command Center:** Hosted at the Gandhinagar Data Center, running the master PostGIS registry, match engine, and unified GIS dashboard.

- **GPU/Accelerator Requirements:**
  Scaling to 80,000 streams relies on the NVIDIA L4 Tensor Core GPU. At ~80 streams per L4, the state requires an estimated total of 1,000 GPUs, distributed evenly as ~166 GPUs per Regional Data Center (approximately 21 standard 2U servers per region).

- **Expected Network Bandwidth and Low-Bandwidth Strategies:**
  Centralizing 80k raw streams would consume ~320 Gbps. By adopting a metadata-first architecture, local edge nodes and regional clusters transmit only JSON metadata, slashing central WAN consumption to approximately **1.6 Gbps**. Full evidentiary video clips are pulled strictly on-demand.

- **Hot/Warm/Cold Storage Assumptions:**
  Processing ~14.2 Million daily ANPR events necessitates a 3-tier strategy:
  - **Hot Tier (0-3 Days):** 10TB NVMe SSD array for active alerts and caching.
  - **Warm Tier (30 Days):** 50TB Ceph Object Storage for full ANPR history.
  - **Cold Tier (1-3 Years):** 1PB AWS S3 Glacier/Tape for evidentiary video and felony archival.

- **Load Balancing, Horizontal Scaling, Monitoring, Logging, Health Checks:**
  The system currently implements a basic health check endpoint (`services/api/routes/health.py`) and standard Python logging in the AI workers. Comprehensive horizontal scaling, per-region layer-7 load balancing (e.g. NGINX/HAProxy), and distributed tracing (e.g. Prometheus/Grafana) are **planned architecture targets**, not yet active in the current PoC.

- **High Availability, Backup, Disaster Recovery, Cybersecurity Controls:**
  The HLD designs for an Active-Active deployment between Gandhinagar and GIFT City, targeting an RPO < 5s and RTO < 60s. Network isolation via GSWAN and mTLS node authentication are documented standards but remain architectural targets to be realized during production deployment.

- **Estimated Implementation and Operational Costs:**
  *Estimated — to be refined with vendor quotes during PoC.*
  A rough order-of-magnitude estimate for the compute layer (1,000 NVIDIA L4 GPUs at ~$2,500 list price each) is ~$2.5M USD for hardware. Accompanied by 6 regional data center setups, 1PB cold storage, and networking hardware, total initial infrastructure CapEx is roughly estimated at $4M - $6M USD. (Note: These figures are indicative industry averages and require formal OEM bidding).

---

## System Architecture

                                STATEWIDE CCTV SOURCES
    [Departmental IP/Analog Cameras] [RTO Testing Tracks] [Public-Facing Private Feeds]
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           EDGE INGESTION & ANALYTICS LAYER                              │
│                                                                                         │
│  ┌───────────────────────┐   ┌────────────────────────────┐   ┌──────────────────────┐  │
│  │ RTSP Stream Ingest    │──▶│ YOLOv8 Vehicle Tracking    │──▶│ EasyOCR Engine       │  │
│  │ (Forced TCP, PTS Sync)│   │ (Confidence ≥ 0.3, IoU 0.5)│   │ (Dynamic ROI Crop)   │  │
│  └───────────────────────┘   └────────────────────────────┘   └──────────┬───────────┘  │
│                                                                          │              │
│                                                                          ▼              │
│                                                               ┌──────────────────────┐  │
│                                                               │ Plate Normalizer     │  │
│                                                               │ (Syntax Correction)  │  │
│                                                               └──────────┬───────────┘  │
└──────────────────────────────────────────────────────────────────────────┼──────────────┘
│ Lightweight
│ Telemetry (JSON)
▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              CENTRAL CORE SERVICES & CLOUD                              │
│                                                                                         │
│  ┌────────────────────────────────────────┐       ┌──────────────────────────────────┐  │
│  │ FastAPI Central Gateway                │◀─────▶│ Supabase Cloud PostgreSQL        │  │
│  │ - Async HTTP Connection Pooling        │       │ - IPv4 Transaction Pooler (:6543)│  │
│  │ - Task Reference Retention (No GC Leak)│       │ - Spatial Tables & Watchlists    │  │
│  │ - Real-time WebSocket Event Dispatcher │       │ - Multi-department Metadata Registry│
│  └───────────────────┬────────────────────┘       └──────────────────────────────────┘  │
└──────────────────────┼──────────────────────────────────────────────────────────────────┘
│ WebSocket Broadcasts
▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        COMMAND & CONTROL DASHBOARD (NEXT.JS)                            │
│                                                                                         │
│  ┌────────────────────────────────────────┐       ┌──────────────────────────────────┐  │
│  │ Statewide GIS Map (Leaflet / OSM)      │       │ Live Alert & Telemetry Drawer    │  │
│  │ - Clustered & Scattered CCTV Assets    │       │ - Sub-second Watchlist Triggers  │  │
│  │ - Route Reconstruction Visualizer      │       │ - Health & Status Indicators     │  │
│  └────────────────────────────────────────┘       └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘

---

## Directory Structure

```text
Gujarat-Hackathon/
├── apps/
│   └── web/                           # Next.js 14 GIS Command Dashboard
│       ├── src/
│       │   ├── components/
│       │   │   ├── map/
│       │   │   │   ├── GujaratCCTVMap.tsx       # Leaflet GIS Map with OSM Tiles
│       │   │   │   ├── CameraDetailDrawer.tsx   # Asset Metadata & Live Player
│       │   │   │   └── RouteVisualizer.tsx      # Cross-Camera Tracking Visuals
│       │   │   └── alerts/
│       │   │       ├── AlertFeed.tsx            # Live WebSocket Alert Feed
│       │   │       └── AlertDetailModal.tsx     # Extended Alert Intel
│       └── package.json
├── packages/
│   └── shared/
│       ├── database.py                # PostgreSQL PostGIS Async Connection Pooler
│       └── models.py                  # Pydantic Schemas & ORM Definitions
├── services/
│   ├── ai/                            # Edge Vision Analytics Engine
│   │   ├── main.py                    # FastApi AI Telemetry Ingestion & Broadcaster
│   │   ├── tracker_manager.py         # YOLOv8 Vehicle Tracking Loop
│   │   ├── anpr_manager.py            # EasyOCR Dynamic Crop Reader
│   │   ├── plate_normalizer.py        # Indian State-Code Transliteration Engine
│   │   ├── ingest_worker.py           # PTS-Compliant RTSP Stream Consumer
│   │   └── itd_yolov8.pt              # Trained Object Detection Weights
│   ├── api/                           # Central Core VMS Backend
│   │   ├── main.py                    # Core Router, WebSockets & Event Dispatcher
│   │   └── routes/
│   │       ├── cameras.py             # CCTV Registry Endpoints (Model 1)
│   │       ├── alerts.py              # Watchlist Match Alerts
│   │       └── stream.py              # MJPEG / HLS Proxy Relay
│   └── ingestion/
│       └── video_reader.py            # Hardened Video Ingestion Adapter
├── scripts/
│   └── test_e2e.py                    # 6-Suite Automated System Health Test
├── database/
│   ├── migrations/
│   │   └── 01_initial_schema.sql      # PostGIS Table Definitions
│   └── seed/
│       └── 01_initial_seed.sql        # 30-City Gujarat Camera Asset Seeds
├── catalogue.json                     # Heterogeneous Camera Feed Registry
├── demo_traffic.mp4                   # Simulation Backup Stream
└── README.md
```

---

## Getting Started

### 1. Prerequisites
* Python 3.11+
* Node.js 18+ and `npm`
* PostgreSQL 15+ (or Supabase Account)
* Modern Browser (Chrome, Edge, Firefox)
* Git LFS (Large File Storage)

### 2. Git LFS Initialization (Models & Video)
Before running the database scripts, you must pull the large AI model weights (~114MB) and the simulation video (~2.8MB) which are tracked via Git LFS.
```bash
git lfs install
git lfs pull
```

### 3. Environment Configuration
Create a `.env` file in the root directory:

```env
# Database (Supabase IPv4 Transaction Pooler)
DATABASE_URL="postgresql+asyncpg://postgres.<PROJECT-ID>:<PASSWORD>@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"

# Operational Mode (Set to true for demo resilience, false for live RTSP)
ENABLE_SIMULATION=true
USE_FALLBACK=true

# Port Configuration
API_PORT=8000
AI_PORT=8002
WEB_PORT=3000
```

### 4. Database Initialization
Run the initialization scripts in your Supabase SQL Editor:

* `database/migrations/01_initial_schema.sql` (Creates cameras, alerts, and watchlist tables).
* `database/seed/01_initial_seed.sql` (Seeds 30+ geographically distributed cameras across Gujarat).

### 5. Running the Platform
Open four terminal windows:

**Terminal 1: Core API Backend**
```bash
$env:PYTHONPATH="."
services\api\venv\Scripts\python -m services.api.main
```

**Terminal 2: Ingestion Service**
```bash
$env:PYTHONPATH="."
services\ingestion\venv\Scripts\python -m services.ingestion.main
```

**Terminal 3: AI Edge Sentinel**
```bash
$env:PYTHONPATH="."
services\ai\venv\Scripts\python -m services.ai.main
```

**Terminal 4: Next.js Command Dashboard**
```bash
cd apps/web
npm install
npm run dev
```

Visit `http://localhost:3000` to interact with the live command center.

### Verification & Automated Testing
Run the automated end-to-end verification script:

```bash
$env:PYTHONPATH="."
services\api\venv\Scripts\python scripts\test_e2e.py
```

**Expected Output**
```text
==================================================
  VIGILIS AUTOMATED END-TO-END SMOKE TEST SUITE   
==================================================
Ensuring services are reachable...

[PASS] [TEST 1] Camera Registry - Found 30 cameras in registry
[PASS] [TEST 2] Health Telemetry - Health telemetry verified (Real health endpoint reachable)
[PASS] [TEST 3] Plate Normalization - Canonical resolution to GJ01ER8842 verified
[PASS] [TEST 4] Route Reconstruction - Reconstructed route with 0 nodes
[PASS] [TEST 5] Report Generation - CSV and PDF report generations succeeded
[PASS] [TEST 6] Video Stream Availability - MJPEG boundary bytes verified

==================================================
ALL TESTS PASSED SUCCESSFULLY! System is ready for production.
```
