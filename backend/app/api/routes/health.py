from fastapi import APIRouter
import os
import json
from datetime import datetime

router = APIRouter()


def get_rate_limit_status():
    """Get current rate limit status."""
    counter_file = "/tmp/request_counter.json"
    try:
        if os.path.exists(counter_file):
            with open(counter_file, 'r') as f:
                data = json.load(f)
                return {
                    "month": data.get("month"),
                    "requests_used": data.get("count", 0),
                    "requests_limit": 2_000_000,
                    "requests_remaining": max(0, 2_000_000 - data.get("count", 0))
                }
    except Exception:
        pass
    return {
        "month": datetime.utcnow().strftime("%Y-%m"),
        "requests_used": 0,
        "requests_limit": 2_000_000,
        "requests_remaining": 2_000_000
    }


@router.get("/health")
async def health_check():
    """Health check endpoint with rate limit status."""
    return {
        "status": "healthy",
        "rate_limit": get_rate_limit_status(),
        "free_tier_protection": "enabled"
    }
