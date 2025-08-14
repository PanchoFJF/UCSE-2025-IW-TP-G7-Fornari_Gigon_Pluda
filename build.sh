#!/usr/bin/env bash
set -o errexit

# install dependencies
uv sync

# move to Django project folder
cd $(dirname $(find . | grep manage.py$))

# collect static files
uv run ./manage.py collectstatic --no-input

# migrate database
uv run ./manage.py migrate

# create superuser if it doesn't exist
uv run ./manage.py createsuperuser --username admin3 --email "juanmagigon@gmail.com" --noinput || true