#!/bin/sh
set -e # Останавливает выполнение скрипта, если любая команда завершится с ошибкой

echo "Starting Flask application container..."

# Устанавливаем необходимые переменные окружения для Flask.
export FLASK_APP=run.py
export FLASK_ENV=production

echo "Running database migrations..."

# Проверяем наличие папки migrations. Если ее нет, инициализируем миграции.
if [ ! -d "./migrations" ]; then
  echo "Migrations directory not found, initializing..."
  flask db init
  flask db migrate -m "Initial migration"
fi

# Применяем все ожидающие миграции к базе данных.
flask db upgrade

echo "Starting Gunicorn server..."

# Запускаем Flask-приложение с использованием Gunicorn.
# Привязываем Gunicorn к порту 5000 на всех доступных сетевых интерфейсах.
# Указываем Gunicorn использовать фабричную функцию create_app из модуля app.
exec gunicorn --bind 0.0.0.0:5000 "app:create_app()"