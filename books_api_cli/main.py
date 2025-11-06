from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, select

from .database import create_db_and_tables, get_session
from .models import Book, BookCreate, BookRead


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code: Create database and tables
    create_db_and_tables()
    yield
    # Shutdown code: (none needed here)


# Create FastAPI app
app = FastAPI(
    title="Books API",
    description="A simple REST API for managing books",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Root endpoint to check if the API is running."""
    return {"message": "Welcome to the Books API!"}


@app.post("/books/", response_model=BookRead)
async def create_book(book: BookCreate, session: Session = Depends(get_session)):
    """Create a new book"""
    db_book = Book.model_validate(book)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@app.get("/books/", response_model=List[BookRead])
async def get_books(session: Session = Depends(get_session)):
    """Get all books"""
    statement = select(Book)
    books = session.exec(statement).all()
    return books


@app.get("/books/{book_id}", response_model=BookRead)
async def get_book(book_id: int, session: Session = Depends(get_session)):
    """Get a book by ID."""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
