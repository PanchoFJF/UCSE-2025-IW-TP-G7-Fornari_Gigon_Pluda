FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY uv.lock ./

RUN pip install uv
RUN uv sync --frozen --no-dev

COPY parroquiaproject/ ./parroquiaproject/
WORKDIR /app/parroquiaproject

# carpeta para base de datos persistente
RUN mkdir -p /data

EXPOSE 8000

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]