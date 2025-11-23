from contextlib import asynccontextmanager
from datetime import timedelta
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlmodel import Session, select

from .database import create_db_and_tables, get_session
from .models import Book, BookCreate, BookRead, BookUpdate
from .security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_api_key_or_token,
    limiter,
)


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
    A comprehensive REST API for managing books with authentication and rate limiting.

    ## Features

    * **Create** books with validation
    * **Read** books with pagination and search
    * **Update** books (partial updates supported)
    * **Delete** books
    * **Search** by title or author
    * **Pagination** support
    * **API Key Authentication**
    * **JWT Bearer Token** authentication
    * **Rate Limiting** for API protection

    ## Authentication

    Two methods available:
    1. **API Key**: Include `X-API-Key` header with your API key
    2. **JWT Token**: Include `Authorization: Bearer <token>` header

    Get a token from `/auth/token` endpoint.
    """,
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Root", "description": "Root endpoints"},
        {"name": "Authentication", "description": "Authentication endpoints"},
        {"name": "Books", "description": "Book management operations"},
    ],
)


# Manually configure security schemes in OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API Key for authentication",
        },
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT Bearer token authentication",
        },
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


# Public endpoints
@app.get("/", tags=["Root"])
@limiter.limit("100/minute")
async def root(request: Request):
    """Root endpoint to check if the API is running."""
    return {
        "message": "Welcome to the Books API!",
        "version": "1.0.0",
        "docs": "/docs",
        "authentication": "This API supports API Key and JWT Bearer Token",
    }


@app.post("/auth/token", tags=["Authentication"])
@limiter.limit("5/minute")
async def login(request: Request, username: str, password: str):
    """
    Get a JWT access token.

    For demo purposes, use:
    - username: admin
    - password: admin

    In production, validate against a user database.
    """
    # Demo credentials (replace with database lookup in production)
    if username == "admin" and password == "admin":
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
    raise HTTPException(
        status_code=401,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.post(
    "/books/",
    response_model=BookRead,
    tags=["Books"],
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Invalid credentials"},
    },
    dependencies=[Security(get_api_key_or_token)],
)
@limiter.limit("10/minute")
async def create_book(
    request: Request,
    book: BookCreate,
    session: Session = Depends(get_session),
):
    """Create a new book (requires authentication via API Key or JWT token)"""
    db_book = Book.model_validate(book)
    session.add(db_book)
    session.commit()
    session.refresh(db_book)
    return db_book


@app.get("/books/", response_model=List[BookRead], tags=["Books"])
@limiter.limit("30/minute")
async def get_books(
    request: Request,
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

    # Add search filter if query is provided
    if q:
        statement = statement.where(
            (Book.title.contains(q)) | (Book.author.contains(q))
        )

    # Add pagination
    statement = statement.offset(offset).limit(limit)

    books = session.exec(statement).all()
    return books


@app.get("/books/{book_id}", response_model=BookRead, tags=["Books"])
@limiter.limit("30/minute")
async def get_book(
    request: Request, book_id: int, session: Session = Depends(get_session)
):
    """Get a book by ID."""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.put(
    "/books/{book_id}",
    response_model=BookRead,
    tags=["Books"],
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Invalid credentials"},
        404: {"description": "Book not found"},
    },
    dependencies=[Security(get_api_key_or_token)],
)
@limiter.limit("10/minute")
async def update_book(
    request: Request,
    book_id: int,
    book_update: BookUpdate,
    session: Session = Depends(get_session),
):
    """Update an existing book (requires authentication)"""
    # Get the existing book
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Update only the fields that were provided
    update_data = book_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)

    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@app.delete(
    "/books/{book_id}",
    tags=["Books"],
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Invalid credentials"},
        404: {"description": "Book not found"},
    },
    dependencies=[Security(get_api_key_or_token)],
)
@limiter.limit("10/minute")
async def delete_book(
    request: Request,
    book_id: int,
    session: Session = Depends(get_session),
):
    """Delete a book by ID (requires authentication)"""
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    session.delete(book)
    session.commit()
    return {"message": f"Book with ID {book_id} has been deleted"}
