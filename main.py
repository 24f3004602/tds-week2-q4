import os
import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# Connect to Redis using the compose service name "redis"
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@app.post("/hit/{key}")
def hit(key: str):
    """Atomically increment the counter for key in Redis."""
    count = r.incr(key)
    return {"key": key, "count": count}


@app.get("/count/{key}")
def count(key: str):
    """Return current counter; 0 if key has never been hit."""
    val = r.get(key)
    return {"key": key, "count": int(val) if val is not None else 0}


@app.get("/healthz")
def healthz():
    """Ping Redis and report status."""
    try:
        r.ping()
        return {"status": "ok", "redis": "up"}
    except redis.ConnectionError:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "redis": "down"}
        )
