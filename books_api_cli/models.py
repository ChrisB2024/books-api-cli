from typing import Optional

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
