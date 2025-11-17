from pytest_httpx import HTTPXMock
from typer.testing import CliRunner

from books_api_cli.cli.main import app

runner = CliRunner()


class TestCLICommands:
    """Test class for CLI commands."""

    def test_create_book_success(self, httpx_mock: HTTPXMock):
        """Test creating a book via CLI."""
        # Mock the API response
        httpx_mock.add_response(
            method="POST",
            url="http://127.0.0.1:8000/books/",
            json={
                "id": 1,
                "title": "Test Book",
                "author": "Test Author",
                "year": 2024,
                "price": 19.99,
            },
            status_code=200,
        )

        # Run the CLI command
        result = runner.invoke(
            app,
            [
                "create",
                "--title",
                "Test Book",
                "--author",
                "Test Author",
                "--year",
                "2024",
                "--price",
                "19.99",
            ],
        )

        assert result.exit_code == 0
        assert "Book created successfully" in result.stdout
        assert "Test Book" in result.stdout

    def test_create_book_validation_error(self, httpx_mock: HTTPXMock):
        """Test creating a book with validation error."""
        # Mock the API error response
        httpx_mock.add_response(
            method="POST",
            url="http://127.0.0.1:8000/books/",
            json={"detail": "Validation error"},
            status_code=422,
        )

        result = runner.invoke(
            app,
            [
                "create",
                "--title",
                "Test",
                "--author",
                "Test",
                "--year",
                "2024",
                "--price",
                "19.99",
            ],
        )

        assert result.exit_code == 1
        assert "Error" in result.stdout

    def test_list_books_success(self, httpx_mock: HTTPXMock):
        """Test listing books via CLI."""
        # Mock the API response
        httpx_mock.add_response(
            method="GET",
            url="http://127.0.0.1:8000/books/?limit=10&offset=0",
            json=[
                {
                    "id": 1,
                    "title": "Book 1",
                    "author": "Author 1",
                    "year": 2023,
                    "price": 19.99,
                },
                {
                    "id": 2,
                    "title": "Book 2",
                    "author": "Author 2",
                    "year": 2024,
                    "price": 29.99,
                },
            ],
            status_code=200,
        )

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "Book 1" in result.stdout
        assert "Book 2" in result.stdout

    def test_list_books_empty(self, httpx_mock: HTTPXMock):
        """Test listing books when no books exist."""
        # Mock empty response
        httpx_mock.add_response(
            method="GET",
            url="http://127.0.0.1:8000/books/?limit=10&offset=0",
            json=[],
            status_code=200,
        )

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 0
        assert "No books found" in result.stdout

    def test_list_books_with_search(self, httpx_mock: HTTPXMock):
        """Test listing books with search query."""
        httpx_mock.add_response(
            method="GET",
            url="http://127.0.0.1:8000/books/?limit=10&offset=0&q=Python",
            json=[
                {
                    "id": 1,
                    "title": "Python Programming",
                    "author": "John Doe",
                    "year": 2023,
                    "price": 29.99,
                }
            ],
            status_code=200,
        )

        result = runner.invoke(app, ["list", "--q", "Python"])

        assert result.exit_code == 0
        assert "Python Programming" in result.stdout

    def test_get_book_success(self, httpx_mock: HTTPXMock):
        """Test getting a specific book."""
        httpx_mock.add_response(
            method="GET",
            url="http://127.0.0.1:8000/books/1",
            json={
                "id": 1,
                "title": "Test Book",
                "author": "Test Author",
                "year": 2024,
                "price": 19.99,
            },
            status_code=200,
        )

        result = runner.invoke(app, ["get", "1"])

        assert result.exit_code == 0
        assert "Test Book" in result.stdout
        assert "Test Author" in result.stdout

    def test_get_book_not_found(self, httpx_mock: HTTPXMock):
        """Test getting a non-existent book."""
        httpx_mock.add_response(
            method="GET",
            url="http://127.0.0.1:8000/books/999",
            json={"detail": "Book not found"},
            status_code=404,
        )

        result = runner.invoke(app, ["get", "999"])

        assert result.exit_code == 1
        assert "not found" in result.stdout

    def test_update_book_success(self, httpx_mock: HTTPXMock):
        """Test updating a book."""
        httpx_mock.add_response(
            method="PUT",
            url="http://127.0.0.1:8000/books/1",
            json={
                "id": 1,
                "title": "Updated Title",
                "author": "Test Author",
                "year": 2024,
                "price": 29.99,
            },
            status_code=200,
        )

        result = runner.invoke(app, ["update", "1", "--price", "29.99"])

        assert result.exit_code == 0
        assert "updated successfully" in result.stdout

    def test_delete_book_with_confirmation(self, httpx_mock: HTTPXMock):
        """Test deleting a book with yes flag."""
        httpx_mock.add_response(
            method="DELETE",
            url="http://127.0.0.1:8000/books/1",
            json={"message": "Book with ID 1 has been deleted"},
            status_code=200,
        )

        result = runner.invoke(app, ["delete", "1", "--yes"])

        assert result.exit_code == 0
        assert "deleted" in result.stdout

    def test_api_connection_error(self, httpx_mock: HTTPXMock):
        """Test handling API connection errors."""
        import httpx

        # Don't mock any response - simulate connection error
        httpx_mock.add_exception(
            httpx.ConnectError("Connection refused"),
            url="http://127.0.0.1:8000/books/?limit=10&offset=0",
        )

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 1
        assert "Error connecting to API" in result.stdout
