from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from .database import create_db_and_tables, get_session
from .models import Book, BookCreate, BookRead, BookUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code: Create database and tables
    create_db_and_tables()
    yield
    # Shutdown code: (none needed here)


# Create FastAPI app
app = FastAPI(
    title="Books API",
    description="""
    A comprehensive REST API for managing books.

    ## Features

    * **Create** books with validation
    * **Read** books with pagination and search
    * **Update** books (partial updates supported)
    * **Delete** books
    * **Search** by title or author
    * **Pagination** support

    ## Usage

    You can use this API to manage a collection of books with full CRUD operations.
    """,
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with custom response."""
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "error_type": "validation_error",
            "message": "Request validation failed",
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with custom response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_type": "error",
            "message": "An error occurred",
        },
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint to check if the API is running."""
    return {"message": "Welcome to the Books API!"}


@app.post("/books/", response_model=BookRead, tags=["Books"])
async def create_book(book: BookCreate, session: Session = Depends(get_session)):
    """Create a new book"""
    db_book = Book.model_validate(book)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@app.get("/books/", response_model=List[BookRead], tags=["Books"])
async def get_books(
    limit: int = 10,
    offset: int = 0,
    q: str = None,
    session: Session = Depends(get_session),
):
    """Get books with pagination and search.
    - **limit**: Number of books to return (default: 10)
    - **offset**: Number of books to skip (default: 0)
    - **q**: Search query to filter books by title or author
    """
    # Start with base query
    statement = select(Book)

    # Add search filter if query if provided
    if q:
        statement = statement.where(
            (Book.title.contains(q)) | (Book.author.contains(q))
        )

    # Add pagination
    statement = statement.offset(offset).limit(limit)

    books = session.exec(statement).all()
    return books


@app.get("/books/{book_id}", response_model=BookRead, tags=["Books"])
async def get_book(book_id: int, session: Session = Depends(get_session)):
    """Get a book by ID."""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.put("/books/{book_id}", response_model=BookRead, tags=["Books"])
async def update_book(
    book_id: int, book_update: BookUpdate, session: Session = Depends(get_session)
):
    """Update an existing book.
    Only provide the fields you want to update. All fields are optional.
    """
    # Get the existing book
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Update on the fields that were provided
    update_data = book_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)

    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@app.delete("/books/{book_id}", tags=["Books"])
async def delete_book(book_id: int, session: Session = Depends(get_session)):
    """Delete a book by ID.
    This operation is irreversible."""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    session.delete(book)
    session.commit()
    return {"message": f"Book with ID {book_id} has been deleted"}
