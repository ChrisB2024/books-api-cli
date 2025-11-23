# Books API CLI

[![CI](https://github.com/ChrisB2024/books-api-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/ChrisB2024/books-api-cli/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A complete REST API and CLI tool for managing a book collection, built with FastAPI, Typer, and SQLModel.

## Features

- 📚 **Full CRUD Operations** - Create, Read, Update, Delete books
- 🔍 **Search & Pagination** - Find books quickly with search and pagination support
- 🖥️ **CLI Interface** - Manage books from the command line
- 🌐 **REST API** - RESTful API with automatic interactive documentation
- ✅ **Comprehensive Tests** - Full test coverage for API and CLI
- 🚀 **CI/CD** - Automated testing with GitHub Actions
- 📊 **Data Validation** - Robust validation with Pydantic models

## Security & Best Practices

### Environment Variables

Copy `.env.example` to `.env` and configure

## Design Decisions & Trade-offs

### Why SQLite?
**Pros:**
- Zero configuration
- Perfect for learning and small-scale apps
- Single file database (portable)

**Cons:**
- Not ideal for high-concurrency production
- Limited compared to PostgreSQL/MySQL

**For Production:** Migrate to PostgreSQL or MySQL by updating `DATABASE_URL`.

### Why FastAPI?
**Pros:**
- Automatic API documentation
- Fast performance (async support)
- Modern Python features (type hints)
- Great for APIs

**Cons:**
- Learning curve for async patterns
- Smaller ecosystem than Django

### Why Typer for CLI?
**Pros:**
- Built on Click (battle-tested)
- Type hints for validation
- Automatic help generation
- Great UX

**Cons:**
- Less features than argparse for complex CLIs

### Monorepo Structure
**Current:** API + CLI in one repo

**Pros:**
- Easier to develop and share code
- Single source of truth
- Simple deployment

**Cons:**
- Larger deployments (both API and CLI)
- Can't version independently

**Alternative:** Split into separate repos for API and CLI packages.

## Roadmap

### v0.2.0 (Next Release)
- [ ] Add authentication (API keys or JWT)
- [ ] Implement rate limiting
- [ ] Add book categories/tags
- [ ] Export/import books (JSON, CSV)
- [ ] Add book cover image URLs

### v0.3.0 (Future)
- [ ] PostgreSQL support
- [ ] Docker containerization
- [ ] GraphQL API endpoint
- [ ] Web frontend (React/Vue)
- [ ] Book recommendations
- [ ] User accounts and permissions

### v1.0.0 (Production)
- [ ] Full authentication system
- [ ] Production deployment guide
- [ ] Performance optimizations
- [ ] Comprehensive monitoring
- [ ] API versioning
- [ ] CDN for static assets

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Make sure:
- Tests pass (`make test`)
- Code is formatted (`make format`)
- Linting passes (`make lint`)

## Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Install from source

```bash
cp.env.example .env
# Clone the repository
git clone https://github.com/ChrisB2024/books-api-cli.git
cd books-api-cli

# Install dependencies
make dev
# or
pip install -e ".[dev]"
