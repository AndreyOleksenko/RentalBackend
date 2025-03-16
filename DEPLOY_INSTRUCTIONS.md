# Инструкции по деплою на Render

## 1. Обновите файл settings.py

Добавьте в начало файла `RentalService/settings.py`:

```python
import dj_database_url
```

## 2. Обновите настройки базы данных в settings.py

Замените настройки DATABASES на:

```python
# Настройка базы данных с поддержкой DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'rentdb_4v87'),
            'USER': os.environ.get('DB_USER', 'rentdb_4v87_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'r6aqq5Thow7CDPDvxEpI3QgbTpZNedjV'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
```

## 3. Настройки в панели управления Render

### Настройки веб-сервиса:

- **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- **Start Command**: `cd /opt/render/project/src && gunicorn RentalService.wsgi:application`

### Переменные окружения:

- `SECRET_KEY`: [ваш секретный ключ]
- `DEBUG`: False
- `ALLOWED_HOSTS`: .onrender.com,localhost,127.0.0.1
- `CORS_ALLOWED_ORIGINS`: https://your-frontend-domain.netlify.app,http://localhost:3000
- `DATABASE_URL`: [URL вашей PostgreSQL базы данных на Render]

## 4. После успешного деплоя

После успешного деплоя выполните миграции базы данных:

1. Зайдите в Shell консоль Render
2. Выполните команды:
   ```
   cd /opt/render/project/src
   python manage.py migrate
   python manage.py createsuperuser
   ```

## Решение проблемы с ModuleNotFoundError

Если вы все еще получаете ошибку `ModuleNotFoundError: No module named 'RentalService'`, попробуйте следующее:

1. Создайте файл `wsgi.py` в корне проекта со следующим содержимым:

```python
import os
import sys

# Добавляем текущую директорию в путь Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RentalService.settings')

application = get_wsgi_application()
```

2. Измените команду запуска в Render на:
   ```
   gunicorn wsgi:application
   ``` 