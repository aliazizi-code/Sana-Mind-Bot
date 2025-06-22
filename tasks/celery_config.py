import os
import redis as rd
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

celery_app  = Celery(
    "SANA",
    broker=os.getenv("REDIS_BROKER", 'redis://localhost:6379/0'),
    backend=os.getenv("REDIS_BACKEND", 'redis://localhost:6379/1'),
)

redis_conn = rd.StrictRedis(host=os.getenv("REDIS_HOST", 'localhost'), port=6379, db=2)

import tasks.ai_analysis
