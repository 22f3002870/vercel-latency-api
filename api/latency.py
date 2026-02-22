from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import numpy as np
import os

app = FastAPI()

# ✅ Proper CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Load telemetry data
with open(os.path.join(os.path.dirname(__file__), "../data.json")) as f:
    data = json.load(f)

@app.post("/api/latency")
async def get_latency(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 0)

    result = {}

    for region in regions:
        records = [r for r in data if r["region"] == region]

        if not records:
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        result[region] = {
            "avg_latency": round(float(np.mean(latencies)), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(float(np.mean(uptimes)), 2),
            "breaches": sum(1 for r in records if r["latency_ms"] > threshold)
        }

    return JSONResponse(
        content=result,
        headers={"Access-Control-Allow-Origin": "*"}
    )

# ✅ Catch-all error handler (ensures header always included)
@app.exception_handler(Exception)
async def all_exception_handler(request: Request, exc: Exception):
    status_code = exc.status_code if hasattr(exc, 'status_code') else 500
    detail = exc.detail if hasattr(exc, 'detail') else str(exc)

    return JSONResponse(
        status_code=status_code,
        content={"detail": detail},
        headers={"Access-Control-Allow-Origin": "*"}
    )
