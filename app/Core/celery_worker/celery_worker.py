# Import Celery for task queue management
from celery import Celery
from ...Core.config import BACKEND,BROKER

# Initialize a Celery app with a custom name "worker"
# BROKER is the message broker URL (e.g., Redis or RabbitMQ)
# BACKEND is the result backend to store task results (e.g., Redis, RPC, database)
celery_app = Celery(
    "worker",
    broker=BROKER,
    backend=BACKEND
)


# Automatically discover and register tasks from the specified module path
# This allows Celery to find all task functions defined under 'download.py'
celery_app.autodiscover_tasks([
    "app.Core.Service.download",
])