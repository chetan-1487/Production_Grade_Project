from fastapi import FastAPI
from app.Router import create_user, post,user_login
from app.Database.models.model import Base
from .Database.database import engine
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app=FastAPI()


origins = [
    "http://localhost:3000",  # Your frontend URL (e.g., React or Vue)
    "https://myfrontend.com",  # Add other allowed origins if needed
]

# Add CORSMiddleware to allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # This allows only specific origins
    allow_credentials=True,  # Allow credentials like cookies and sessions
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def root():
    return {
        "message": "Welcome to the YouTube Downloader API",
        "status": "Running"
    }


app.include_router(post.router)
app.include_router(user_login.router)
app.include_router(create_user.router)