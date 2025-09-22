#!/usr/bin/env bash
# exit on error
set -o errexit

# Запуск Django приложения с Gunicorn
gunicorn Snippets.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120