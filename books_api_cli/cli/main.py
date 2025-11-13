import os
from typing import Optional

import httpx
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Load environment variables
load_dotenv()

# Get API base URL from environment
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Create Typer app
app = typer.Typer(
    name="books",
    help="CLI tool for managing books via the Books API",
    add_completion=False,
)

# Create Rich console for pretty output
console = Console()


@app.command()
def create(
    title: str = typer.Option(..., "--title", "-t", help="Book title"),
    author: str = typer.Option(..., "--author", "-a", help="Book author"),
    year: int = typer.Option(..., "--year", "-y", help="Publication year"),
    price: float = typer.Option(..., "--price", "-p", help="Book price"),
):
    """Create a new book."""
    try:
        # Prepare book data
        book_data = {
            "title": title,
            "author": author,
            "year": year,
            "price": price,
        }

        # Make POST request to API
        response = httpx.post(f"{API_BASE_URL}/books/", json=book_data)
        response.raise_for_status()

        # Get the created book
        book = response.json()

        # Display success message
        console.print("✅ [green]Book created successfully![/green]")
        console.print(f"ID: {book['id']}")
        console.print(f"Title: {book['title']}")
        console.print(f"Author: {book['author']}")
        console.print(f"Year: {book['year']}")
        console.print(f"Price: ${book['price']:.2f}")

    except httpx.HTTPStatusError as e:
        detail = e.response.json().get("detail", "Unknown error")
        console.print(f"❌ [red]Error: {detail}[/red]")
        raise typer.Exit(code=1) from None
    except httpx.RequestError as e:
        console.print(f"❌ [red]Error connecting to API: {e}[/red]")
        console.print(f"💡 Make sure the API is running at {API_BASE_URL}")
        raise typer.Exit(code=1) from None


@app.command()
def list(
    q: Optional[str] = typer.Option(None, "--q", "-q", help="Search query"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of books to return"),
    offset: int = typer.Option(0, "--offset", "-o", help="Number of books to skip"),
):
    """List all books with optional search and pagination."""
    try:
        # Prepare query parameters
        params = {"limit": limit, "offset": offset}
        if q:
            params["q"] = q

        # Make GET request to API
        response = httpx.get(f"{API_BASE_URL}/books/", params=params)
        response.raise_for_status()

        # Get the books
        books = response.json()

        if not books:
            console.print("📚 [yellow]No books found.[/yellow]")
            return

        # Create a table for nice display
        table = Table(title=f"Books (showing {len(books)})")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="green")
        table.add_column("Author", style="magenta")
        table.add_column("Year", style="blue")
        table.add_column("Price", style="yellow")

        # Add rows to table
        for book in books:
            table.add_row(
                str(book["id"]),
                book["title"],
                book["author"],
                str(book["year"]),
                f"${book['price']:.2f}",
            )

        # Display the table
        console.print(table)

    except httpx.HTTPStatusError as e:
        detail = e.response.json().get("detail", "Unknown error")
        console.print(f"❌ [red]Error: {detail}[/red]")
        raise typer.Exit(code=1) from None
    except httpx.RequestError as e:
        console.print(f"❌ [red]Error connecting to API: {e}[/red]")
        raise typer.Exit(code=1) from None


@app.command()
def get(book_id: int = typer.Argument(..., help="Book ID")):
    """Get a specific book by ID."""
    try:
        # Make GET request to API
        response = httpx.get(f"{API_BASE_URL}/books/{book_id}")
        response.raise_for_status()

        # Get the book
        book = response.json()

        # Display book details
        console.print("\n📖 [bold cyan]Book Details[/bold cyan]\n")
        console.print(f"[cyan]ID:[/cyan] {book['id']}")
        console.print(f"[green]Title:[/green] {book['title']}")
        console.print(f"[magenta]Author:[/magenta] {book['author']}")
        console.print(f"[blue]Year:[/blue] {book['year']}")
        console.print(f"[yellow]Price:[/yellow] ${book['price']:.2f}\n")

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            console.print(f"❌ [red]Book with ID {book_id} not found.[/red]")
        else:
            detail = e.response.json().get("detail", "Unknown error")
            console.print(f"❌ [red]Error: {detail}[/red]")
        raise typer.Exit(code=1) from None
    except httpx.RequestError as e:
        console.print(f"❌ [red]Error connecting to API: {e}[/red]")
        raise typer.Exit(code=1) from None


@app.command()
def update(
    book_id: int = typer.Argument(..., help="Book ID"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Book title"),
    author: Optional[str] = typer.Option(None, "--author", "-a", help="Book author"),
    year: Optional[int] = typer.Option(None, "--year", "-y", help="Publication year"),
    price: Optional[float] = typer.Option(None, "--price", "-p", help="Book price"),
):
    """Update an existing book (only provide fields you want to update)."""
    try:
        # Prepare update data (only include provided fields)
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if author is not None:
            update_data["author"] = author
        if year is not None:
            update_data["year"] = year
        if price is not None:
            update_data["price"] = price

        if not update_data:
            msg = "No fields to update. Please provide at least one field."
            console.print(f"❌ [red]{msg}[/red]")
            raise typer.Exit(code=1)

        # Make PUT request to API
        url = f"{API_BASE_URL}/books/{book_id}"
        response = httpx.put(url, json=update_data)
        response.raise_for_status()

        # Get the updated book
        book = response.json()

        # Display success message
        console.print("✅ [green]Book updated successfully![/green]")
        console.print(f"ID: {book['id']}")
        console.print(f"Title: {book['title']}")
        console.print(f"Author: {book['author']}")
        console.print(f"Year: {book['year']}")
        console.print(f"Price: ${book['price']:.2f}")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            console.print(f"❌ [red]Book with ID {book_id} not found.[/red]")
        else:
            detail = e.response.json().get("detail", "Unknown error")
            console.print(f"❌ [red]Error: {detail}[/red]")
        raise typer.Exit(code=1) from None
    except httpx.RequestError as e:
        console.print(f"❌ [red]Error connecting to API: {e}[/red]")
        raise typer.Exit(code=1) from None


@app.command()
def delete(
    book_id: int = typer.Argument(..., help="Book ID"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Delete a book by ID."""
    try:
        # Confirmation prompt (unless --yes flag is used)
        if not yes:
            msg = f"Are you sure you want to delete book with ID {book_id}?"
            confirm = typer.confirm(msg)
            if not confirm:
                console.print("❌ [yellow]Deletion cancelled.[/yellow]")
                raise typer.Exit(code=0)

        # Make DELETE request to API
        response = httpx.delete(f"{API_BASE_URL}/books/{book_id}")
        response.raise_for_status()

        # Display success message
        result = response.json()
        console.print(f"✅ [green]{result['message']}[/green]")

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            console.print(f"❌ [red]Book with ID {book_id} not found.[/red]")
        else:
            detail = e.response.json().get("detail", "Unknown error")
            console.print(f"❌ [red]Error: {detail}[/red]")
        raise typer.Exit(code=1) from None
    except httpx.RequestError as e:
        console.print(f"❌ [red]Error connecting to API: {e}[/red]")
        raise typer.Exit(code=1) from None
