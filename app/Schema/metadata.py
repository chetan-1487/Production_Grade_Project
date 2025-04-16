from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
from uuid import UUID as uuid
import re


YOUTUBE_URL_REGEX = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/(watch\?v=)?[\w\-]{11}(&[a-zA-Z0-9_]+=[a-zA-Z0-9_&\-]*)*$"
)
YOUTUBE_PLAYLIST_REGEX = re.compile(r"^(https?://)?(www\.)?youtube\.com/playlist\?list=[\w\-]+")

ALLOWED_FORMATS = {"mp4", "webm", "mp3"}

class UserCreate(BaseModel):
    email:str
    password:str

class Userout(BaseModel):
    id:uuid
    email:str
    created_at:datetime

    model_config = ConfigDict(from_attributes=True)
    
class UserLogin(BaseModel):
    email:EmailStr
    password:str

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    id:uuid

class DownloadRequest(BaseModel):
    url:str
    format:str
    quality:str

    @field_validator("url")
    @classmethod
    def validate_youtube_url(cls, value):
        if not YOUTUBE_URL_REGEX.match(value) or YOUTUBE_PLAYLIST_REGEX.match(value):
            raise ValueError("Invalid YouTube URL format.")
        return value
    
    @field_validator("format")
    @classmethod
    def validate_format(cls, value):
        value = value.lower()
        if value not in ALLOWED_FORMATS:
            raise ValueError(f"Invalid format. Allowed formats: {ALLOWED_FORMATS}")
        return value

class VideoMetadataResponse(BaseModel):
    title:str
    duration:str
    views:int
    likes:int
    channel:str
    thumbnail_url:str
    published_date:str