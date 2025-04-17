from fastapi import status, HTTPException, Depends, APIRouter

from ..Database.models import model
from ..Schema import metadata
from ..Utils import utils
from ..Database.database import get_db
from sqlalchemy.orm import Session

# Create an APIRouter instance to handle routes related to users
router=APIRouter(
    prefix="/users",
    tags=['Create User']
)

# ---------------------- Create User ----------------------

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=metadata.Userout)
def create_user(user:metadata.UserCreate,db:Session=Depends(get_db)):   
    # Hash the password before saving it to the database
    # Assuming utils.hash() is a function that hashes the password
    hashed_password=utils.hash(user.password)
    # Update the password in the user object to the hashed password
    user.password=hashed_password

    # Create a new User object using the data from the incoming request
    new_user=model.User(**user.dict())
    # Add the new user to the database session
    db.add(new_user)
    db.commit()
    # Refresh the object to ensure it has the updated information (e.g., the ID)
    db.refresh(new_user)
    return new_user

# ---------------------- Get User by ID ----------------------

@router.get("/{id}",response_model=metadata.Userout)
def get_user(id:str, db:Session=Depends(get_db)):
    # Query the database to find a user by their ID
    user = db.query(model.User).filter(model.User.id==id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"User with id:{id} doesnot exist")
    
    # Return the user (response_model ensures it matches the expected output format) 
    return user