from fastapi import status, HTTPException, Depends, APIRouter

from ..Database.models import model
from ..Schema import metadata
from ..Utils import utils
from ..Database.database import get_db
from sqlalchemy.orm import Session

router=APIRouter(
    prefix="/users",
    tags=['Create User']
)


@router.post("/",status_code=status.HTTP_201_CREATED,response_model=metadata.Userout)
def create_user(user:metadata.UserCreate,db:Session=Depends(get_db)):
    #hash the password = user.password   
    hashed_password=utils.hash(user.password)
    user.password=hashed_password
    new_user=model.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{id}",response_model=metadata.Userout)
def get_user(id:str, db:Session=Depends(get_db)):
    user = db.query(model.User).filter(model.User.id==id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"User with id:{id} doesnot exist")
     
    return user