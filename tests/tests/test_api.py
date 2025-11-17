import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from books_api_cli.database import get_session
from books_api_cli.main import app


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    # Create an in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a TestClient with a dependency override for the database session."""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# Test data
sample_book = {
    "title": "Test Book",
    "author": "Test Author",
    "year": 2024,
    "price": 19.99,
}


class TestBooksAPI:
    """Test class for Books API endpoints."""

    def test_create_root(self, client: TestClient):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to the Books API!"}

    def test_create_book(self, client: TestClient):
        """Test creating a new book."""
        response = client.post("/books/", json=sample_book)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_book["title"]
        assert data["author"] == sample_book["author"]
        assert data["year"] == sample_book["year"]
        assert data["price"] == sample_book["price"]
        assert "id" in data

    def test_get_books(self, client: TestClient):
        """Test reading books when database is empty."""
        response = client.get("/books/")
        assert response.status_code == 200
        assert response.json() == []

    def test_read_books_with_data(self, client: TestClient):
        """Test reading books with data in database."""
        # Create a book first
        client.post("/books/", json=sample_book)

        # Get all books
        response = client.get("/books/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == sample_book["title"]

    def test_read_book_by_id(self, client: TestClient):
        """Test reading a specific book by ID."""
        # Create a book first
        create_response = client.post("/books/", json=sample_book)
        book_id = create_response.json()["id"]

        # Get the book by ID
        response = client.get(f"/books/{book_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == book_id
        assert data["title"] == sample_book["title"]

    def test_read_book_not_found(self, client: TestClient):
        """Test reading a non-existent book by ID."""
        response = client.get("/books/999")
        assert response.status_code == 404
        assert "Book not found" in response.json()["detail"]

    def test_update_book(self, client: TestClient):
        """Test updating an existing book."""
        # Create a book first
        create_response = client.post("/books/", json=sample_book)
        book_id = create_response.json()["id"]

        # Update the book
        update_data = {"title": "Updated Title", "price": 29.99}
        response = client.put(f"/books/{book_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["price"] == 29.99
        assert data["author"] == sample_book["author"]  # Unchanged

    def test_update_book_not_found(self, client: TestClient):
        """Test updating a non-existent book."""
        response = client.put("/books/999", json={"title": "New Title"})
        assert response.status_code == 404

    def test_delete_book(self, client: TestClient):
        """Test deleting a book."""
        # Create a book first
        create_response = client.post("/books/", json=sample_book)
        book_id = create_response.json()["id"]

        # Delete the book
        response = client.delete(f"/books/{book_id}")
        assert response.status_code == 200
        assert f"Book with ID {book_id} has been deleted" in response.json()["message"]

        # Verify it's deleted
        get_response = client.get(f"/books/{book_id}")
        assert get_response.status_code == 404

    def test_delete_book_not_found(self, client: TestClient):
        """Test deleting a non-existent book."""
        response = client.delete("/books/999")
        assert response.status_code == 404

    def test_search_books(self, client: TestClient):
        """Test search books by query."""
        # Create multiple books
        books = [
            {
                "title": "Python Programming",
                "author": "John Doe",
                "year": 2023,
                "price": 29.99,
            },
            {
                "title": "JavaScript Guide",
                "author": "Jane Smith",
                "year": 2022,
                "price": 24.99,
            },
            {
                "title": "Data Science",
                "author": "Python Expert",
                "year": 2024,
                "price": 39.99,
            },
        ]

        for book in books:
            client.post("/books/", json=book)

        # Search for "Python"
        response = client.get("/books/?q=Python")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_pagination(self, client: TestClient):
        """Test pagination functionality."""
        # Create multiple books
        for i in range(10):
            book = {
                "title": f"Book {i}",
                "author": f"Author {i}",
                "year": 2000 + i,
                "price": 10.99 + i,
            }
            client.post("/books/", json=book)

        # Test Limit
        response = client.get("/books/?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Test offset
        response = client.get("/books/?limit=2&offset=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Book 2"

    def test_create_book_validation_error(self, client: TestClient):
        """Test validation errors when creating a book."""
        # Missing required fields
        response = client.post("/books/", json={})
        assert response.status_code == 422

        # Invalid data types
        invalid_book = {
            "title": "Valid Title",
            "author": "Valid Author",
            "year": "not_a_number",
            "price": -5,
        }
        response = client.post("/books/", json=invalid_book)
        assert response.status_code == 422

    def test_update_book_with_invalid_year(self, client: TestClient):
        """Test creating a book with invalid year (future)."""
        invalid_book = {
            "title": "Future Book",
            "author": "Futurist",
            "year": 3000,  # Too far in the future
            "price": 19.99,
        }
        response = client.post("/books/", json=invalid_book)
        assert response.status_code == 422

    def test_create_book_with_negative_price(self, client: TestClient):
        """Test creating a book with negative price."""
        invalid_book = {
            "title": "Free Book",
            "author": "Dumb author",
            "year": 2024,
            "price": -3.00,  # Negative price
        }
        response = client.post("/books/", json=invalid_book)
        assert response.status_code == 422

    def test_create_book_with_empty_title(self, client: TestClient):
        """Test creating a book with an empty title."""
        invalid_book = {
            "title": "",
            "author": "Valid Author",
            "year": 2024,
            "price": 19.99,
        }
        response = client.post("/books/", json=invalid_book)
        assert response.status_code == 422

    def test_create_book_with_no_price(self, client: TestClient):
        """Test creating a book with no price."""
        invalid_book = {
            "title": "Priceless Book",
            "author": "Generous Author",
            "year": 2024,
            "price": None,
        }
        response = client.post("/books/", json=invalid_book)
        assert response.status_code == 422

    def test_update_partial_fields(self, client: TestClient):
        """Test updating only some fields of a book."""
        # Create a book
        create_response = client.post("/books/", json=sample_book)
        book_id = create_response.json()["id"]

        # Update only the price
        response = client.put(f"/books/{book_id}", json={"price": 29.99})
        assert response.status_code == 200
        data = response.json()
        assert data["price"] == 29.99
        assert data["title"] == sample_book["title"]  # Unchanged

    def test_search_case_insensitive(self, client: TestClient):
        """Test that search is case insensitive."""
        # Create a book
        client.post(
            "/books/",
            json={
                "title": "Python Programming",
                "author": "John Doe",
                "year": 2023,
                "price": 29.99,
            },
        )

        # Search with lowercase
        response = client.get("/books/?q=python")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_pagination_edge_cases(self, client: TestClient):
        """Test pagination with edge cases."""
        # Create 3 books
        for i in range(3):
            client.post(
                "/books/",
                json={
                    "title": f"Book {i}",
                    "author": "Author",
                    "year": 2024,
                    "price": 10.0,
                },
            )

        # Test offset beyond available books
        response = client.get("/books/?offset=100")
        assert response.status_code == 200
        assert response.json() == []

        # Test limit of 0
        response = client.get("/books/?limit=0")
        assert response.status_code == 200
        assert len(response.json()) == 0
