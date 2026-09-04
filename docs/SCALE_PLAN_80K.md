# Scaling Strategy: Reaching 80,000 Cameras

## 1. The 80k Scale Problem
Scaling an AI-driven surveillance system to 80,000 cameras is not a software challenge; it is fundamentally a physics and infrastructure challenge.
If all 80,000 cameras transmitted a standard 1080p 25FPS h.264 stream directly to a central cloud, the required bandwidth would be:
`80,000 cameras × 4 Mbps = 320,000 Mbps = ~320 Gbps`
This is physically impossible on the standard Gujarat State Wide Area Network (GSWAN) backbone.

## 2. Bandwidth Optimization: Metadata-First Architecture
We solve this using a **Metadata-First Architecture**.
- **Continuous Feeds Stay Local:** Video streams are kept local at the police station NVR or processed at one of the 6 Regional GPU Clusters.
- **Only Metadata Moves Centrally:** The central Gandhinagar servers only receive JSON text payloads (plate number, timestamp, confidence, camera ID).
- **Bandwidth Math:** `80,000 cameras × 20 Kbps (Metadata) = 1.6 Gbps total statewide WAN usage.`
- **On-Demand Video:** If an alert is triggered (e.g., a Stolen Vehicle is matched), the central server sends a command to the Edge node to pull a highly compressed 10-second evidentiary video clip.

## 3. Tiered Storage Sizing & Equations
With 14.2 Million daily ANPR reads, storage must be rigorously tiered to manage costs.

| Tier | Technology | Retention | Content | Calculated Size Required |
|------|------------|-----------|---------|--------------------------|
| **HOT** | NVMe SSD Array | 3 Days | High-speed cache, active alerts, recent metadata | `14.2M events × 100KB (Metadata+Snapshot) × 3 days ≈ 4.2 TB` (Provision 10TB) |
| **WARM** | Ceph Object Storage | 30 Days | Full ANPR history, analytics aggregates | `14.2M × 100KB × 30 days ≈ 42 TB` (Provision 50TB) |
| **COLD** | AWS S3 Glacier / Tape | 1-3 Years | Evidentiary video clips, felony cases | Assuming 1% of events require 5MB video clips: `142,000 × 5MB × 365 days ≈ 259 TB/year` (Provision 1PB) |

## 4. Compute & GPU Inference Sizing
To process 80,000 streams in real-time without overwhelming a single data center, compute is distributed across 6 Regional Zones (Ahmedabad, Surat, Vadodara, Rajkot, Bhavnagar, Gandhinagar).

**GPU Math (Using NVIDIA L4 Tensor Core GPU):**
- A single NVIDIA L4 using TensorRT and INT8 quantization can process approximately **80 concurrent 1080p streams** at 15 FPS (sufficient for ANPR).
- Total GPUs Required State-Wide = `80,000 streams / 80 streams per GPU = 1,000 L4 GPUs`.
- **Per Region Allocation:** `1,000 GPUs / 6 Zones = ~166 GPUs per Regional Data Center`.
- Assuming 8 GPUs per 2U rack server: `~21 physical servers per region`. This is highly feasible and budget-friendly for state infrastructure.

## 5. High Availability & Disaster Recovery (DR)
- **Active-Active Topology:** Primary Data Center in Gandhinagar, Secondary DR site in GIFT City.
- **Failover:** PostgreSQL uses synchronous logical replication. Kafka implements Multi-Region MirrorMaker.
- **Recovery Targets:** Recovery Point Objective (RPO) < 5 seconds. Recovery Time Objective (RTO) < 60 seconds.
