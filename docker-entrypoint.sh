#!/bin/sh
set -e

python manage.py migrate --noinput

# Опционально: создать суперпользователя из переменных окружения
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py shell <<EOF
from django.contrib.auth import get_user_model
U = get_user_model()
username = "$DJANGO_SUPERUSER_USERNAME"
password = "$DJANGO_SUPERUSER_PASSWORD"
email = "${DJANGO_SUPERUSER_EMAIL:-admin@museum.local}"
u, created = U.objects.get_or_create(username=username, defaults={"email": email, "is_staff": True, "is_superuser": True})
u.set_password(password)
u.is_staff = True
u.is_superuser = True
u.email = email
u.save()
print("superuser ready:", username)
EOF
fi

# Демо-данные (можно отключить: SKIP_DEMO_DATA=1)
if [ "${SKIP_DEMO_DATA:-0}" != "1" ]; then
  python manage.py load_demo_data || true
fi

exec gunicorn MuseumApp.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 2
