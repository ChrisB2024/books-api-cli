from typing import List, Optional

from sqlmodel import Field, SQLModel


# Base class with common fields
class BookBase(SQLModel):
    title: str = Field(
        ..., min_length=1, max_length=200
    )  # The ... makes this field required
    author: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=0, le=2100)
    price: float = Field(..., ge=0)


# Database table model
class Book(BookBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # Primary key field


# Model for creating new book entries
class BookCreate(BookBase):
    pass


# Model for reading book data
class BookRead(BookBase):
    id: int


# Model for updating existing books (all fields optional)
class BookUpdate(SQLModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=0)
    price: Optional[float] = Field(None, ge=0)


# Error response models
class ErrorResponse(SQLModel):
    """Standard error response model."""

    detail: str
    error_type: str = "error"


class ValidationErrorResponse(SQLModel):
    """Validation error response model."""

    detail: List[dict]
    error_type: str = "validation_error"
