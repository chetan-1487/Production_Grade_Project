from pydantic import BaseModel, EmailStr, ConfigDict, field_validator,model_validator,constr
from datetime import datetime
from typing import Optional
from uuid import UUID as uuid
import re

# Regular expression patterns to validate YouTube video and playlist URLs
YOUTUBE_URL_REGEX = re.compile(r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/(watch\?v=)?[\w\-]{11}(&[a-zA-Z0-9_]+=[a-zA-Z0-9_&\-]*)*$")
YOUTUBE_PLAYLIST_REGEX = re.compile(r"^(https?://)?(www\.)?youtube\.com/playlist\?list=[\w\-]+")

# Set of allowed formats for downloading
ALLOWED_FORMATS = {"mp4", "webm", "mp3"}

# Pydantic model to handle user creation (with email and password)
class UserCreate(BaseModel):
    email:EmailStr
    password:str

# Pydantic model for user output (returned after creating a user)
class Userout(BaseModel):
    id:uuid
    email:EmailStr
    created_at:datetime

    # Configure Pydantic to use attribute names as field names (from_attributes=True)
    model_config = ConfigDict(from_attributes=True)

# Pydantic model for user login (email and password)
class UserLogin(BaseModel):
    email:EmailStr
    password:str

# Pydantic model for OAuth2 tokens (access token and token type)
class Token(BaseModel):
    access_token:str
    token_type:str

# Pydantic model for token data, which contains user information extracted from the token
class TokenData(BaseModel):
    id:uuid

# Pydantic model for the download request (url, format, and quality)
class DownloadRequest(BaseModel):
    url:str
    format:str
    quality:str
    start_time: Optional[str]=None
    end_time: Optional[str]=None

    # Validator to ensure that both start_time and end_time are provided if one is given
    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, value):
        if value:  # Validate time format only if the value is not None
            try:
                datetime.strptime(value, "%H:%M:%S")
            except ValueError:
                raise ValueError(f"Invalid time format for {value}. Use HH:MM:SS.")
        return value
    
    # Validator for the 'url' field to check if it is a valid YouTube URL
    @field_validator("url")
    @classmethod
    def validate_youtube_url(cls, value):
        if not YOUTUBE_URL_REGEX.match(value) or YOUTUBE_PLAYLIST_REGEX.match(value):
            raise ValueError("Invalid YouTube URL format.")
        return value
    
    # Validator for the 'format' field to ensure it's one of the allowed formats
    @field_validator("format")
    @classmethod
    def validate_format(cls, value):
        value = value.lower()
        if value not in ALLOWED_FORMATS:
            raise ValueError(f"Invalid format. Allowed formats: {ALLOWED_FORMATS}")
        return value

# Pydantic model for the response returned when querying video metadata
class VideoMetadataResponse(BaseModel):
    title:str
    duration:str
    views:int
    likes:int
    channel:str
    thumbnail_url:str
    published_date:str