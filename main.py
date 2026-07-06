import os
import time
import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# ── Retry connection to Redis at startup ──
r = None
for attempt in range(30):
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
            socket_connect_timeout=2,
        )
        r.ping()
        print(f"Connected to Redis on attempt {attempt + 1}")
        break
    except Exception as e:
        print(f"Redis connection attempt {attempt + 1} failed: {e}")
        time.sleep(1)

if r is None:
    raise RuntimeError("Could not connect to Redis after 30 attempts")


@app.post("/hit/{key}")
def hit(key: str):
    count = r.incr(key)
    return {"key": key, "count": count}


@app.get("/count/{key}")
def count(key: str):
    val = r.get(key)
    return {"key": key, "count": int(val) if val is not None else 0}


@app.get("/healthz")
def healthz():
    try:
        r.ping()
        return {"status": "ok", "redis": "up"}
    except redis.ConnectionError:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "redis": "down"}
        )
