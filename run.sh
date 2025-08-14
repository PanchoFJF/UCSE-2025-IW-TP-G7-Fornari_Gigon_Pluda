#!/usr/bin/env bash
set -o errexit

# move to Django project folder
cd $(dirname $(find . | grep manage.py$))

# run with Gunicorn
uv run gunicorn $(dirname $(find . | grep wsgi.py$) | sed "s/\.\///g").wsgi:application