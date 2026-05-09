from collections import defaultdict
from time import time
from fastapi import HTTPException, Request

_BUCKETS = defaultdict(list)

async def rate_limit_middleware(request: Request, call_next):
    key = request.client.host if request.client else "unknown"
    now = time()
    bucket = [t for t in _BUCKETS[key] if now - t < 60]
    _BUCKETS[key] = bucket
    if len(bucket) >= 120:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    bucket.append(now)
    return await call_next(request)
