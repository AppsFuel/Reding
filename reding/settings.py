import os

DAEMON_CONFIG = {
    'host': os.getenv('REDING_DAEMON_HOST', '0.0.0.0'),
    'port': int(os.getenv('REDING_DAEMON_PORT', 5000)),
}

REDIS_CONFIG = {
    'host': os.getenv('REDING_REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDING_REDIS_PORT', 6379)),
    'db': int(os.getenv('REDING_REDIS_DB', 0)),
    'decode_responses': True,
}

PAGINATION_DEFAULT_OFFSET = 0
PAGINATION_DEFAULT_SIZE = 10
