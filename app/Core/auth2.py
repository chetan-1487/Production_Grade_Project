from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from ..Schema import metadata

from ..Database.models import model
from ..Database import database
from sqlalchemy.orm import Session
from uuid import UUID as uuid

auth2_schema=OAuth2PasswordBearer(tokenUrl="login")

#Secret key to encode and decode JWT tokens
SECRET_KEY="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM="HS256" 
ACCESS_TOKEN_EXPIRE_MINUTES=30

def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.now()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})

    encode_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

    return encode_jwt


def verify_access_token(token:str,credentials_exception):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)

        id:uuid=payload.get("user_id")
        # print("id of user", str(id))

        if id is None:
            raise credentials_exception
        
        token_data=metadata.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    
    return token_data

def get_current_user(token:str=Depends(auth2_schema),db:Session=Depends(database.get_db)):
    credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"Could not validate credentials",headers={"WWW-Authenticate":"Bearer"})

    curr_token=verify_access_token(token,credentials_exception)
    # print(curr_token)

    user= db.query(model.User).filter(model.User.id==curr_token.id).first()
    
    return user

