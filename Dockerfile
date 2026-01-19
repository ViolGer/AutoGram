FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

# uv
RUN pip install --no-cache-dir uv

# сначала манифесты для кеша
COPY pyproject.toml /code/pyproject.toml
COPY uv.lock /code/uv.lock

# ставим зависимости в .venv (как делает uv)
RUN uv sync --frozen --no-dev

# затем код
COPY . /code
