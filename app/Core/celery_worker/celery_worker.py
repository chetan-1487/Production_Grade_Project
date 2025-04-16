from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

celery_app = Celery(
    "worker",
    broker=os.getenv("BROKER"),
    backend=os.getenv("BACKEND")
)

celery_app.autodiscover_tasks([
    "app.Core.Service.download",
])