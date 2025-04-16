from sqlalchemy import Column,Integer,String, ForeignKey, DateTime,Text
from ..database import Base
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID


class User(Base):
    __tablename__="users"
    id=Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,nullable=False)
    email=Column(String,nullable=False,unique=True)
    password=Column(String,nullable=False)
    created_at=Column(DateTime,default=datetime.now())


class VideoMetadata(Base):
    __tablename__="video_metadata"
    id = Column(UUID(as_uuid=True), primary_key=True)
    title=Column(String,nullable=False)
    duration=Column(String,nullable=False)
    views=Column(Integer,nullable=False)
    likes=Column(Integer)
    channel=Column(String,nullable=False)
    thumbnail_url=Column(String,nullable=False)
    published_date=Column(String,nullable=False)
    created_at=Column(DateTime,default=datetime.now())
    user_id=Column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"),nullable=False)


class DownloadHistory(Base):
    __tablename__="download_history"
    id=Column(Integer,primary_key=True,autoincrement=True)
    url=Column(Text,nullable=False)
    download_url=Column(Text,nullable=False)
    status=Column(String,nullable=False)
    video_id=Column(UUID(as_uuid=True),ForeignKey("video_metadata.id",ondelete="CASCADE"),nullable=False)
    user_id=Column(UUID(as_uuid=True),ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    download_at=Column(DateTime,default=datetime.now())
