# Project Delphi Narrative Log (NarrLog)

A lightweight, real-time narrative log service built with **FastAPI** and **PostgreSQL 16**
Designed for multi-user environments where operators need append-only logging, tamper-evident hash chaining, and instant updates via WebSockets.

---

## Features
- Multi-user, real-time log entries (WebSocket broadcast)
- Append-only with hash-chained integrity verification
- Structured tags for REES related Node&Input Codes (Ndd_ddd)
- Simple FastAPI backend, PostGreSQL datastore
- Ready for containerization (Python 3.9 / Kubernetes compatible)

---

## Quick Start (Local)

```powershell
# Clone the repo
git clone https://github.com/MerkoftheBeast/Delphi-NarrLog.git
cd narrative_log

# Create and activate a venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install Dependencies
pip install -r requirements.txt

# Copy and edit environmental variables
copy .env.example .env

# Run the API
uvicorn api.main:app --host 0.0.0.0 --port 8088
