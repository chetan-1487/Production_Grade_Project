from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..Core.config import Database_Connection

conn=Database_Connection

if not conn:
    raise ValueError("Database connection string is missing. Please check your .env file.")

# Create the SQLAlchemy engine to connect to the database using the connection string
engine=create_engine(conn)

# SessionLocal will be used to create session instances for interacting with the database
sessionLocal=sessionmaker(autoflush=False,autocommit=False,bind=engine)

# Base class for our models
Base=declarative_base()

# Dependency function that provides a database session instance
# Use this in FastAPI routes via Depends() to interact with the DB
def get_db():
    # Create a new session
    db=sessionLocal()
    try:
        # Yield the session so it can be used by FastAPI endpoints
        yield db
    finally:
        db.close()