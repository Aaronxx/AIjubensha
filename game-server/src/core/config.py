"""Application configuration."""
import os
from datetime import timedelta

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/aijubensha")

# JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# DeepSeek API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# Game settings
PREPARATION_TIMEOUT_MINUTES = 5
ACT1_TALK_TIMEOUT_MINUTES = 25
ROUND1_SEARCH_TIMEOUT_MINUTES = 10
ACT2_DISCUSS_TIMEOUT_MINUTES = 30
DETECTIVE_VOTE_TIMEOUT_MINUTES = 3
ROUND2_SEARCH_TIMEOUT_MINUTES = 10
ACT3_DISCUSS_TIMEOUT_MINUTES = 30

# AP Settings
ROUND1_AP = 15
ROUND2_AP = 20
DETECTIVE_AP_BONUS = 1

# Speech limits
MAX_SPEECH_PER_ACT = 15
MAX_QUESTIONS_PER_PLAYER = 3
