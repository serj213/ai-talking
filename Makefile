.PHONY: check gen-openapi

gen-openapi:
	uv run python scripts/generate_openapi_contract.py

check: gen-openapi
	uv run pytest
	uv run ruff check .
	uv run mypy src
