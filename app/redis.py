#import os
import redis.asyncio as redis
from app.config import settings

#REDIS_HOST = os.getenv("REDIS_HOST", "redis")
#REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
