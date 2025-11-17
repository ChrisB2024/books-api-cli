.PHONY: help install dev run test test-cov lint format clean

help:
	@echo "Available commands:"
	@echo "  make install    - Install production dependencies"
	@echo "  make dev        - Install development dependencies"
	@echo "  make run        - Run the FastAPI server"
	@echo "  make test       - Run all tests"
	@echo "  make test-cov   - Run tests with coverage report"
	@echo "  make lint       - Run linting checks (ruff)"
	@echo "  make format     - Format code with black and ruff"
	@echo "  make clean      - Remove build artifacts and cache"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

run:
	uvicorn books_api_cli.main:app --reload

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=books_api_cli --cov-report=term-missing --cov-report=html

lint:
	ruff check books_api_cli tests
	black --check books_api_cli tests

format:
	ruff check books_api_cli tests --fix
	black books_api_cli tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
