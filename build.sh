#!/usr/bin/env bash
# exit on error
set -o errexit

# Установка продакшен зависимостей
pip install -r requirements-prod.txt

# Сборка статических файлов для продакшена
echo "Начинаем сборку статических файлов..."
python manage.py collectstatic --noinput --clear

# Проверяем, что статические файлы собраны
echo "Статические файлы собраны в: $(pwd)/staticfiles"
echo "Количество файлов: $(find staticfiles/ -type f | wc -l)"

# Применение миграций
python manage.py migrate