# MuseumApp — веб-сайт музея на Django

Индивидуальное задание: музей (вариант 9). Реализованы сущности предметной области, CRUD, авторизация, разграничение доступа, статистика, два внешних API, тесты и логирование.

## Структура проекта (по аналогии с WeatherApp)

```
MuseumApp/
  manage.py
  MuseumApp/           # конфигурация проекта
    __init__.py
    asgi.py
    settings.py
    urls.py
    wsgi.py
  museum/              # приложение: экспонаты, залы, экскурсии, сотрудники
  pages/                # приложение: главная, новости, отзывы, контакты и т.д.
  templates/
  static/
  media/
```

## Модели (сущности)

- **Музей:** ArtType, Hall, EmployeePosition, Employee (OneToOne User), Visitor (OneToOne User, 18+), Exhibit, Exhibition, ExhibitionExhibit (M2M through), Show, Tour, TicketPrice, TicketPurchase
- **Страницы:** Article, CompanyInfo, News, FAQ, Contact, Vacancy, Review, PromoCode

Связи: OneToOne (User–Employee, User–Visitor), ForeignKey (Exhibit–Hall, Exhibit–Guardian, Tour–Conductor и др.), ManyToMany (Exhibition–Exhibits через ExhibitionExhibit, Show–Exhibits).
## Диаграмма сущностей (ER)

```
[User] 1----1 [Employee] 1----* [Exhibit] (guardian)
                |                    |
                *                    *
[EmployeePosition]              [Hall]
                |                    |
[Employee] *----1 [Hall]        [ArtType] 1----* [Exhibit]
                |
[Tour] *----1 [Employee] (conductor)
[TicketPurchase] *----1 [User], *----1 [Tour]

[Exhibition] M----M [Exhibit] (through ExhibitionExhibit)
[Show] M----M [Exhibit]
```

## Запуск

1. Установка зависимостей: `pip install -r requirements.txt`
2. Миграции: `python manage.py migrate`
3. Суперпользователь: `python manage.py createsuperuser`
4. Демо-данные (≥10 экспонатов): `python manage.py load_demo_data`
5. Сервер: `python manage.py runserver`

Локально — **SQLite**. В Docker/продакшене — **PostgreSQL** (`DATABASE_URL`).

Админка: `/admin/`. Главная: `/`.

## Роли и доступ

- **Superuser:** полная статистика (`/museum/admin/stats/`), CRUD экспонатов, все данные.
- **Сотрудник (User с записью Employee):** «Мои экспонаты», «Мои экскурсии» (личный кабинет).
- **Посетитель (зарегистрированный User с профилем Visitor):** покупка билетов, промокоды, отзывы (18+, телефон +375 (29) XXX-XX-XX).
- **Без регистрации:** залы, экспонаты, экскурсии, новости, отзывы (чтение), тарифы, промокоды.
## Реализовано по заданию

- Модели с типами данных и связями (OneToOne, ForeignKey, ManyToMany); валидация телефона +375 (29) XXX-XX-XX, возраст 18+.
- CRUD экспонатов (создание/редактирование/удаление для админа).
- Все модели в админке, фильтры, инлайны (экспонаты в зале, экспонаты хранителя, экспозиции–экспонаты).
- Авторизация (login/logout, регистрация), разграничение по ролям.
- Поиск и сортировка: экспонаты, залы, экскурсии, отзывы, новости, FAQ.
- Статистика: экспонаты по видам искусства, продажи билетов (сумма, среднее), размер группы (среднее, медиана); для админа — экспонаты по залам после даты, экскурсии по сезонам, сотрудники по этажу.
- Визуализация: диаграмма (полоски) по видам искусства на странице «Статистика».
- Даты: текущая дата и UTC в формате DD/MM/YYYY в подвале и на странице статистики; календарь в текстовом виде (текущий месяц).
- Два внешних API: JSONPlaceholder (пост), Quotable (цитата) — страница «Внешние API».
- API проекта (`/museum/api/exhibits/`) — только для авторизованных (неавторизованным 403).
- URL через `re_path` (регулярные выражения).
- Логирование: уровень из конфигурации (DEBUG/INFO), вывод в консоль и файл `museum.log`.
- Тесты: музей и страницы (модели, представления, валидация, роли). Запуск: `python manage.py test museum pages`.
- Валидация форм: серверная (Django forms + clean), клиентская (форма отзыва — проверка оценки и текста в JS).

## Тесты и покрытие

```bash
python manage.py test museum pages
# С coverage (если установлен):
coverage run --source=museum,pages manage.py test museum pages
coverage report
```

Цель: покрытие 80% и выше (добавляйте тесты при необходимости).

## Дополнительное задание (***)

- **Параллельный код (asyncio):** модуль `museum/parallel_module.py` — параллельный запрос к двум внешним API через `aiohttp`. Страница без CSS: `/museum/parallel-demo/`.
- **Production:** запуск через `gunicorn` (см. `DEPLOY.md`). Настройки: `DJANGO_DEBUG`, `ALLOWED_HOSTS`, `DJANGO_SECRET_KEY`, `DATABASE_URL` (PostgreSQL), `LOGGING_LEVEL`.
- **Docker:** `Dockerfile` + `docker-compose.yml` (web + PostgreSQL). Локально: `docker-compose up --build`.
- **Облако:** инструкции по Render, Railway и др. — в **`DEPLOY.md`**. Проект должен быть на GitHub с доступом для `@AnnBsuir`.
## Файлы конфигурации

- `MuseumApp/settings.py` — LOGGING_LEVEL, LOGGING, API_ANONYMOUS_RATE, MEDIA, STATIC, TIME_ZONE (Europe/Minsk), LANGUAGE_CODE (ru-ru).
