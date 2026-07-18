# Развёртывание MuseumApp (дополнительное задание)

## 1. Параллельный код (asyncio)

В проекте есть модуль **`museum/parallel_module.py`**: запросы к двум внешним API (JSONPlaceholder и Quotable) выполняются **параллельно** через `asyncio` и `aiohttp`. На странице «Внешние API» при установленном пакете `aiohttp` используется эта реализация; иначе — последовательный вызов из `services.py`.

Установка: `pip install aiohttp` (уже в `requirements.txt`).

---

## 2. Запуск API в production режиме

Локально (без Docker):

```bash
# Переменные для production
export DJANGO_DEBUG=0
export ALLOWED_HOSTS=localhost,127.0.0.1
export DJANGO_SECRET_KEY=ваш-секретный-ключ

python manage.py collectstatic --noinput
gunicorn MuseumApp.wsgi:application --bind 0.0.0.0:8000 --workers 2
```

Статика отдаётся через **WhiteNoise** (уже в `settings.py`). Для продакшена задайте `DJANGO_DEBUG=0` и свой `DJANGO_SECRET_KEY`.

---

## 3. Dockerfile

Сборка и запуск образа:

```bash
docker build -t museumapp .
docker run -p 8000:8000 -e DJANGO_DEBUG=0 -e DJANGO_SECRET_KEY=ваш-ключ museumapp
```

Внутри контейнера выполняются `migrate` и запуск **gunicorn**.

---

## 4. docker-compose (локальный запуск с PostgreSQL)

```bash
docker-compose up --build
```

Сервисы: `web` (Django/gunicorn) + `db` (PostgreSQL 16). Приложение: http://localhost:8000

Переменная `DATABASE_URL=postgres://museum:museum@db:5432/museum` включает PostgreSQL.

**Публикация образа для преподавателя (Docker Hub):**

```bash
docker-compose build
docker tag museumapp_web:latest ВАШ_ЛОГИН/museumapp:latest
docker push ВАШ_ЛОГИН/museumapp:latest
```

Преподаватель может запустить так (нужен также Postgres или полный compose):

```bash
docker-compose up
# или
docker run -p 8000:8000 -e DATABASE_URL=... ВАШ_ЛОГИН/museumapp:latest
```

---

## 5. Развёртывание в облаке

Рекомендуется сначала изучить бесплатные квоты, чтобы не выходить на платные тарифы.

### Бесплатные квоты (ориентировочно)

| Провайдер | Бесплатный уровень |
|-----------|--------------------|
| **Heroku** | Нет бесплатного tier с 2022; платные планы от ~$5/мес |
| **Railway** | Около $5 кредитов в месяц, затем оплата |
| **Render** | Бесплатный web-сервис (spin down при неактивности), бесплатная БД |
| **Fly.io** | Небольшие бесплатные ресурсы (VM, объём) |
| **AWS** | Free tier 12 месяцев (EC2, RDS и др. — с ограничениями) |
| **GCP** | Кредиты при регистрации, бесплатный tier с лимитами |
| **Azure** | Кредиты при регистрации, бесплатные сервисы с лимитами |

### Heroku (если используете платный план)

1. Установите [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli).
2. В корне проекта создайте **Procfile**:
   ```
   web: gunicorn MuseumApp.wsgi:application --bind 0.0.0.0:$PORT
   ```
3. Укажите версию Python в **runtime.txt**:
   ```
   python-3.12.0
   ```
4. В админке Heroku задайте переменные: `DJANGO_SECRET_KEY`, `ALLOWED_HOSTS` (ваш домен и `*.herokuapp.com`), `DJANGO_DEBUG=0`.
5. Деплой: `git push heroku main` (или через GitHub интеграцию).

### Render — из Docker Hub (без GitHub, если образ уже опубликован)

1. Зарегистрируйтесь / войдите на [render.com](https://render.com).
2. **New → PostgreSQL** (Free), имя например `museum-db`. Скопируйте **Internal Database URL**.
3. **New → Web Service → Existing Image**:
   - Image URL: `docker.io/ВАШ_ЛОГИН/museumapp:latest`
4. Environment:
   - `DJANGO_DEBUG=0`
   - `LOGGING_LEVEL=INFO`
   - `ALLOWED_HOSTS=.onrender.com`
   - `DJANGO_SECRET_KEY` — Generate / свой секрет
   - `DATABASE_URL` — Internal Database URL из шага 2
   - `DJANGO_SUPERUSER_USERNAME=museum_admin`
   - `DJANGO_SUPERUSER_PASSWORD=MuseumAdmin2026!`
   - `DJANGO_SUPERUSER_EMAIL=admin@museum.local`
5. Create Web Service → дождитесь Deploy.
6. Откройте URL вида `https://museumapp-xxxx.onrender.com`  
   Админка: `/admin/` (логин `museum_admin`).

### Render — из GitHub (Blueprint)

После создания приватного репозитория (см. `GITHUB_SETUP.md`):

1. New → Blueprint → выберите репозиторий с `render.yaml`.
2. Render создаст Postgres + Web Service автоматически.
3. Добавьте env: `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD`.

### Railway

1. [railway.app](https://railway.app) → New Project → Deploy from GitHub.
2. Укажите корень проекта, добавьте переменные окружения.
3. В настройках сервиса задайте команду запуска: `gunicorn MuseumApp.wsgi:application --bind 0.0.0.0:$PORT`.

Во всех вариантах в **ALLOWED_HOSTS** нужно указать хост, который выдаёт облако (например, `yourapp.render.com`, `yourapp.railway.app`).
