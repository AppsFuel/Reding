import os
import redis
rclient = redis.StrictRedis(
    host=os.getenv('REDING_TEST_REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDING_TEST_REDIS_PORT', 6379)),
    db=int(os.getenv('REDING_TEST_REDIS_DB', 15)),
    decode_responses=True,
)
