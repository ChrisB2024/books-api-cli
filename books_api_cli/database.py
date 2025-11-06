import os
from typing import Generator

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

# load environment variables from .env file
load_dotenv()

# Get database URL from environement or use default SQLite URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./books.db")

# Create database engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Shows SQL queries in console for debugging
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)


# Function to create database and tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Dependency to get a database session
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
