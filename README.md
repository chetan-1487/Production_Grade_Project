
# YouTube Downloader API

A production-grade REST API built using **FastAPI** that allows users to download YouTube videos and retrieve related metadata by providing a YouTube video URL. The API supports multiple video formats (MP4, WEBM, MKV), audio-only downloads (MP3), and metadata retrieval. It is designed to be scalable, secure, and optimized for performance.

---

## Features

- **Video Download**: Download videos in various formats (MP4, WEBM, MKV) and quality levels (360p to 4K).
- **Audio-Only Download**: Download audio as MP3.
- **Metadata Retrieval**: Retrieve video metadata (title, duration, views, likes, channel, etc.).
- **Optimized Performance**: The API is designed to be fast and efficient with background processing and caching mechanisms.
- **Scalable & Secure**: Built to handle a large number of requests with secure, rate-limited access to prevent misuse.

---

## Installation

### Prerequisites

- Python 3.9 or later
- PostgreSQL database for storing metadata and download history
- Redis (optional, for caching and background tasks with Celery)
- A virtual environment is recommended.

### Step 1: Clone the repository

```bash
git clone https://github.com/yourusername/youtube-downloader-api.git
cd youtube-downloader-api
```

### Step 2: Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set up PostgreSQL

1. Create a PostgreSQL database and user.
2. Configure the `DATABASE_URL` in the `.env` file.
   - Example `.env` file:

   ```env
   DATABASE_URL=postgresql://username:password@localhost/dbname
   BROKER=redis://localhost:6379/0  # Optional, for Celery
   BACKEND=redis://localhost:6379/0
   ```

### Step 5: Run database migrations

```bash
alembic upgrade head
```

### Step 6: Start the FastAPI server

```bash
uvicorn app.main:app --reload
```

---

## API Endpoints

### 1. **Download Video**

- **URL**: `/download`
- **Method**: `POST`
- **Description**: Download a YouTube video in the requested format and quality.
- **Request Body**:

   ```json
   {
     "url": "https://www.youtube.com/watch?v=example",
     "format": "mp4",  // "mp4", "webm", "mkv"
     "quality": "720p"  // "360p", "480p", "720p", "1080p", "4k"
   }
   ```

- **Response**:

   ```json
   {
     {
      "Status": "Success",
      "filepath": "Downloads/e9e0132a-d740-4936-89f8-acdb2d20ff7a.mp4",
      "title": "Diljit Dosanjh - G.O.A.T.",
      "duration": "3m43s",
      "views": 3142,
      "likes": 27,
      "channel": "Diljit",
      "thumbnail_url": "https://i.ytimg.com/vi_webp/cl0a3i2wFcc/maxresdefault.webp",
      "published_date": "2020-07-29"
    }
   }
   ```

### 2. **Download Audio**

- **URL**: `/download/audio`
- **Method**: `POST`
- **Description**: Download audio from a YouTube video as MP3.
- **Request Body**:

   ```json
   {
     "url": "https://www.youtube.com/watch?v=example",
     "format": "mp3",  // "mp3"
     "quality": "720p"  // "360p", "480p", "720p", "1080p", "1440p", "4k" (optional)
   }
   ```

- **Response**:

   ```json
   {
     {
      "Status": "Success",
      "filepath": "/Downloads/e9e0132a-d740-4936-89f8-acdb2d20ff7a.mp4",
      "title": "Diljit Dosanjh - G.O.A.T.",
      "duration": "3m43s",
      "views": 3142,
      "likes": 27,
      "channel": "Diljit",
      "thumbnail_url": "https://i.ytimg.com/vi_webp/cl0a3i2wFcc/maxresdefault.webp",
      "published_date": "2020-07-29"
    }
   }
   ```

  ### 3. **Get Download History**

- **URL**: `/history`
- **Method**: `GET`
- **Description**: Retrieve download history of a YouTube video by URL.

- **Response**:

   ```json
  [
  {
    "url": "https://www.youtube.com/watch?v=",
    "status": "Success",
    "download_at": "2025-04-16T05:07:15.582276",
    "download_url": "/Downloads/e9e0132a-d740-4936-89f8-acdb2d20ff7a.mp4"
  },
  {
    "url": "https://www.youtube.com/watch?",
    "status": "Success",
    "download_at": "2025-04-16T05:07:15.665886",
    "download_url": "/Downloads/f5a6c733-bee0-4232-a81f-cbfadd5d4577.mp4"
  },
  {
    "url": "https://www.youtube.com/watch?v=",
    "status": "Success",
    "download_at": "2025-04-16T05:07:15.737902",
    "download_url": "/Downloads/b45ba9bf-c555-4264-ab5e-8daec61eb9ec.mp4"
  },
  {
    "url": "https://www.youtube.com/watch?v=cl0",
    "status": "Success",
    "download_at": "2025-04-16T05:07:15.798351",
    "download_url": "/Downloads/87351e0a-99f5-4eb3-ae3b-beff2b38734d.mp4"
  },
  ]
   ```

---

## Database Schema

### Video Metadata

- `id`: UUID (Primary Key)
- `title`: String
- `duration`: String (Format: HH:MM:SS)
- `views`: Integer
- `likes`: Integer
- `channel`: String
- `thumbnail_url`: String
- `published_date`: Date
- `created_at`: Timestamp
- `user_id`: UUID (Foreign Key to Users Table)

### Download History

- `id`: UUID (Primary Key)
- `status`: String (e.g., "completed", "failed")
- `video_id`: UUID (Foreign Key to `VideoMetadata`)
- `download_date`: Timestamp

---

## Background Tasks

For download processing and handling long-running tasks, **Celery** with **Redis** is used. To start Celery, run:

```bash
celery -A app.Core.celery_worker.celery_worker.celery_app worker --loglevel=info
```

---

## Security

- Rate limiting: The API uses basic rate limiting to prevent abuse.
- CORS: Cross-Origin Resource Sharing (CORS) is configured to allow the frontend to communicate with the API securely.
- JWT-based Authentication (Optional): If user authentication is required, the API supports JWT tokens for secure access.

---

## Performance Optimization

- **Caching**: Results (such as video metadata) are cached using Redis to reduce redundant database queries.
- **Asynchronous Tasks**: Downloads and metadata retrieval are processed asynchronously to ensure non-blocking API responses.

---

## Contributions

Contributions are welcome! Please open an issue or submit a pull request.

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Submit a pull request.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
