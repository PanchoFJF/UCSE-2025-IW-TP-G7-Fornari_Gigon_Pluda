FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de configuración
COPY pyproject.toml ./
COPY uv.lock ./

# Instalar dependencias del proyecto
RUN pip install uv
RUN uv sync --frozen --no-dev

# Copiar el resto del proyecto
COPY parroquiaproject/ ./parroquiaproject/
WORKDIR /app/parroquiaproject

# Crear carpeta para base de datos persistente
RUN mkdir -p /data

EXPOSE 8000

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]