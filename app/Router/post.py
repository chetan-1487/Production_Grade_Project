from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter,Query
from app.Database.models.model import User
from ..Core import auth2
from sqlalchemy.orm import Session
from ..Database.database import get_db
from ..Schema.metadata import DownloadRequest
from ..Core.Service.download import download_video
from app.Database.models.model import VideoMetadata,DownloadHistory
from datetime import datetime,timedelta
from dotenv import load_dotenv
import os
from sqlalchemy import func, and_

load_dotenv()

DOWNLOAD_LIMIT = int(os.getenv("DOWNLOAD_LIMIT_PER_DAY"))

router=APIRouter(
    tags=['User Information']
)

@router.get("/history")
def get_download_history(db: Session = Depends(get_db),current_user:int=Depends(auth2.get_current_user)):
    history = db.query(DownloadHistory).all()

    if not history:
        raise HTTPException(status_code=404, detail="No download history found")

    return [
        {
            "url": item.url,
            "status": item.status,
            "download_at": item.download_at,
            "download_url": item.download_url,
        }
        for item in history
    ]


# @router.get("/metadata", response_model=VideoMetadataResponse)
# def get_video_metadata(url: str = Query(..., description="YouTube video URL"), db: Session = Depends(get_db),current_user:int=Depends(auth2.get_current_user)):
#     metadata = db.query(VideoMetadata).filter(VideoMetadata.url == url).first()

#     if not metadata:
#         raise HTTPException(status_code=404, detail="Video metadata not found")

#     return {
#         "title": metadata.title,
#         "duration": metadata.duration,
#         "views": metadata.views,
#         "likes": metadata.likes,
#         "channel": metadata.channel,
#         "thumbnail_url": metadata.thumbnail_url,
#         "published_date": metadata.published_date
#     }

@router.post("/download")
async def download(request: DownloadRequest, db: Session = Depends(get_db),current_user:User=Depends(auth2.get_current_user)):

    today = datetime.utcnow().date()
    start_of_day = datetime(today.year, today.month, today.day)
    end_of_day = start_of_day + timedelta(days=1)

    # 2. Count user’s downloads today
    download_count = db.query(func.count(DownloadHistory.id)).filter(
        and_(
            DownloadHistory.user_id == current_user.id,
            DownloadHistory.download_at >= start_of_day,
            DownloadHistory.download_at < end_of_day
        )
    ).scalar()

    if download_count >= DOWNLOAD_LIMIT:
        raise HTTPException(
            status_code=403,
            detail="Daily download limit reached. Login with another account or try again tomorrow."
        )

    task_result = download_video.delay(request.url, request.quality, request.format)

    try:
        result = task_result.get(timeout=99999999999)
        if not isinstance(result, list):
            result = [result]  # wrap single video result in a list
        # filepath, metadata_dict = result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading video: {str(e)}")
    
    if not result:
        raise HTTPException(status_code=400, detail="Download failed")
    
    responses=[]

    # if not filepath:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Download failed")

    # # Store metadata in DB
    # metadata = VideoMetadata(**metadata_dict)
    # metadata.user_id=current_user.id
    # db.add(metadata)
    # db.commit()
    # db.refresh(metadata)

    # # print(current_user)

    # # Store metadata in DownloadHistory
    # history = DownloadHistory(
    #     url=request.url,
    #     video_id=metadata_dict["id"],
    #     status="Success",
    #     download_at=datetime.utcnow(),
    #     download_url=filepath
    # )
    # history.user_id=current_user.id
    # db.add(history)
    # db.commit()
    # db.refresh(history)

    # return{
    #     "Status":"Success",
    #     "filepath": filepath,
    #     "title": metadata.title,
    #     "duration": metadata.duration,
    #     "views": metadata.views,
    #     "likes": metadata.likes,
    #     "channel": metadata.channel,
    #     "thumbnail_url": metadata.thumbnail_url,
    #     "published_date": metadata.published_date
    # }

    for filepath, metadata_dict in result:
        if not filepath:
            continue

        # Store metadata in DB
        metadata = VideoMetadata(**metadata_dict)
        metadata.user_id = current_user.id
        db.add(metadata)
        db.commit()
        db.refresh(metadata)

        # Store download history
        history = DownloadHistory(
            url=request.url,
            video_id=metadata_dict["id"],
            status="Success",
            download_at=datetime.utcnow(),
            download_url=filepath,
            user_id=current_user.id
        )
        db.add(history)
        db.commit()
        db.refresh(history)

        responses.append({
            "Status": "Success",
            "filepath": filepath,
            "title": metadata.title,
            "duration": metadata.duration,
            "views": metadata.views,
            "likes": metadata.likes,
            "channel": metadata.channel,
            "thumbnail_url": metadata.thumbnail_url,
            "published_date": metadata.published_date
        })

    return {"downloaded_videos": responses}