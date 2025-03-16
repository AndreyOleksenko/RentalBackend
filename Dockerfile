FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Создаем скрипт для запуска
RUN echo '#!/bin/bash\n\
python manage.py migrate --noinput\n\
python manage.py collectstatic --noinput\n\
gunicorn --bind 0.0.0.0:8000 RentalService.wsgi:application' > /app/entrypoint.sh \
&& chmod +x /app/entrypoint.sh

# Открытие порта
EXPOSE 8000

# Запуск сервера через скрипт
CMD ["/app/entrypoint.sh"]
