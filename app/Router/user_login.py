from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter

from ..Database.models import model
from ..Schema import metadata
from ..Utils import utils
from ..Core import auth2
from ..Database.database import get_db
from sqlalchemy.orm import Session
from typing import List
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router=APIRouter(
    tags=["User Login"]
)

@router.post("/login")
def login(user_credentials:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user = db.query(model.User).filter(model.User.email==user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email and passsword")
    access_token=auth2.create_access_token(data={"user_id":str(user.id)})
    return {"access_token":access_token, "token_type":"bearer","User_id":user.id}