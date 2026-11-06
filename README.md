# Talking Agent backend

Backend голосового агента для практики разговорного английского.

Глобальный roadmap продукта описан в [PRODUCT_PLAN.md](PRODUCT_PLAN.md).

## Требования

- Python 3.13
- uv

## Установка

```text
uv sync --locked --all-groups
```

## Проверки

```text
uv run pytest
uv run ruff check .
uv run mypy src
make gen-openapi
make check
```

## Запуск

```text
uv run talking-agent
```
