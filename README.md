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

## Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Install from source

```bash
# Clone the repository
git clone https://github.com/ChrisB2024/books-api-cli.git
cd books-api-cli

# Install dependencies
make dev
# or
pip install -e ".[dev]"
