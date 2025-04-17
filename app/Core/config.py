from dotenv import load_dotenv
import os
load_dotenv()

Database_Connection=os.getenv("Database_Connection")
BROKER=os.getenv("BROKER")
BACKEND=os.getenv("BACKEND")

DOWNLOAD_LIMIT_PER_DAY=int(os.getenv("DOWNLOAD_LIMIT_PER_DAY"))


# Duration in seconds (5 hours)
MAX_DURATION=int(os.getenv("MAX_DURATION"))

# Size in bytes (3 GB)
MAX_SIZE=int(os.getenv("MAX_SIZE"))
