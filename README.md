# Talking Agent backend

Backend голосового агента для практики разговорного английского.

## Требования

- Python 3.13
- uv

## Установка

```text
uv sync --locked --all-groups
cp .env.example .env
```

API-ключи задаются в локальном `.env`. Этот файл не добавляется в Git.

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
