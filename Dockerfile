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

# Carpeta de datos persistente
RUN mkdir -p /data
VOLUME ["/data"]

EXPOSE 8000

CMD bash -c " \
    if [ ! -f /data/db.sqlite3 ] && [ -f db.sqlite3 ]; then \
        echo 'Copiando base de datos inicial a /data...'; \
        cp db.sqlite3 /data/db.sqlite3; \
    fi && \
    ln -sf /data/db.sqlite3 db.sqlite3 && \
    uv run python manage.py runserver 0.0.0.0:8000"