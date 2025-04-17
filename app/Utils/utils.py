from passlib.context import CryptContext

# Create a CryptContext object to manage password hashing algorithms (using bcrypt)
pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to hash the password
def hash(password:str):
    # Hash the provided password using bcrypt (which is more secure than plain hashes)
    return pwd_context.hash(password)

# Function to verify if the provided plain password matches the stored hashed password
def verify(plain_password,hashed_password):
    # Check if the plain password matches the hashed password using bcrypt
    return pwd_context.verify(plain_password,hashed_password)