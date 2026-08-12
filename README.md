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
  pages/               # приложение: главная, новости, отзывы, контакты и т.д.
  templates/
  static/
    css/               # стили (ЛР2, ЛР3)
    js/                # скрипты (ЛР3)
    images/
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
4. Демо-данные (≥10 экспонатов, контактов и услуг): `python manage.py load_demo_data`
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

---

## Лабораторные работы (STRWEB)

Проект развивается поэтапно: **ЛР1 (HTML)** → **ЛР2 (CSS)** → **ЛР3 (JavaScript)**. Тема сайта — **музей** (вариант 9).

### ЛР1 — HTML и семантическая вёрстка

Базовая структура сайта на Django-шаблонах без Bootstrap.

**Реализовано:**

- Семантическая разметка: `header`, `nav`, `main`, `aside`, `footer`, `article`, `section`, `figure`, `address`, `time`, `blockquote` и др.
- Базовый шаблон `templates/base.html`: горизонтальная и вертикальная навигация, Schema.org (`Museum`), meta-теги, favicon.
- Главная страница: баннеры, каталог услуг, партнёры, стихотворный блок, последняя статья.
- Страницы: о компании (история, видео, реквизиты, сертификат), новости, словарь (FAQ), контакты, вакансии, отзывы, промокоды, политика конфиденциальности.
- Раздел музея: экспонаты, залы, экскурсии, экспозиции, тарифы, корзина, оформление заказа.
- Таблицы в БД и вывод данных: контакты, новости, FAQ, вакансии, отзывы, тарифы (≥10 экспонатов в демо-данных).
- Формы: регистрация, вход, отзыв, оформление покупки — с серверной валидацией.
- Корзина на сессиях, маршруты услуг и checkout.
- Команда `load_demo_data` для наполнения БД.

**Ключевые файлы:** `templates/`, `pages/models.py`, `museum/models.py`, `pages/views.py`, `museum/views.py`.

---

### ЛР2 — CSS (каскадные таблицы стилей)

Стилизация без Bootstrap — только собственные CSS-файлы.

**Реализовано:**

- `static/css/base.css` — CSS custom properties, типографика (Cinzel + Source Sans 3), сетка layout-wrapper, header/aside/main, формы, таблицы, ссылки, footer-preloader.
- Отдельные файлы для страниц в `static/css/pages/`:
  - `home.css` — CSS-анимация зала галереи, прелоадер главной страницы;
  - `about.css` — блоки о компании, история, сертификат (border-image, watermark);
  - `news.css` — карточки новостей, многоколоночный текст статьи;
  - `faq.css` — аккордеон `<details>`/`<summary>`;
  - `contacts.css` — карточки сотрудников, карта;
  - `vacancies.css`, `reviews.css`, `promo.css`, `catalog.css`, `privacy.css`, `exhibitions.css`.
- Подключение через `{% block page_css %}` в шаблонах.
- Адаптивность: media queries для планшетов и мобильных устройств.
- Декоративные элементы: `::before`/`::after`, градиенты, тени, hover-эффекты.
- Статические ресурсы: логотип, баннеры, картины галереи, SVG-сертификат.

**Ключевые файлы:** `static/css/`, `templates/base.html`, `templates/includes/`.

---

### ЛР3 — JavaScript (интерактивность)

Интерактивность средствами JS. Задания, не связанные напрямую с UI сайта, вынесены на отдельную страницу **«Задания JS»** (`/js-lab/`).

**Реализовано на сайте:**

| № | Задание | Страница / файлы |
|---|---------|------------------|
| 1 | Слайдер изображений (класс `ImageSlider`) | `/` — `static/js/slider.js`, настройки loop/navs/pags/auto/delay |
| 2 | Переключатель темы (светлая/тёмная), localStorage | Весь сайт — `static/js/theme.js` |
| 3 | Интерактивная таблица контактов | `/contacts/table/` — сортировка, фильтр, пагинация, добавление, API `/api/contacts/` |
| 4 | Генератор `<textarea>` с атрибутами | `/about/` — `static/js/form-generator.js`, localStorage |
| 5 | Клиентская пагинация каталога (3/5/10 на страницу) | `/museum/ticket-prices/` — `catalog-pagination.js` |
| 6 | 3D-эффект объёма при наведении на карточки | Главная, каталог — `card-3d.js` |
| 7 | Проверка даты рождения, возраст, день недели | `/register/`, `/js-lab/` — `age-check.js` |
| 11 | Scroll-анимация статуй (приближение и масштаб) | `/about/` — `scroll-statues.js` |

**Страница «Задания JS» (`/js-lab/`):**

| № | Задание | Файлы |
|---|---------|-------|
| 8 | Классы и игрушки: прототипное наследование и `class`/`extends` | `toys-prototype.js`, `toys-class.js`, `toys-ui.js` |
| 9 | Web API: геолокация, синтез речи, Battery API | `apis-demo.js` |
| 10 | Chart.js: график arccos(x) (ряд vs Math.acos), сохранение PNG | `chart-arccos.js` |

**Дополнительно:**

- Тёмная тема (`data-theme="dark"`, классы `.dark-theme`/`.night-mode`) с переопределениями для таблиц, карточек, форм, разделов новостей, словаря, контактов, отзывов, вакансий, промокодов — файлы `*-dark.css`, подключаются через `lr3.css`.
- Прелоадер при загрузке данных таблицы контактов — `preloader-util.js`.
- Валидация URL и телефона при добавлении контакта — `validators.js`.
- Демо-данные: ≥12 контактов и ≥12 услуг/тарифов.

**Структура JS:**

```
static/js/
  slider.js           # задание 1
  theme.js            # задание 2
  contacts-table.js   # задание 3
  validators.js
  preloader-util.js
  form-generator.js   # задание 4
  catalog-pagination.js  # задание 5
  card-3d.js          # задание 6
  age-check.js        # задание 7
  toys-prototype.js   # задание 8
  toys-class.js
  toys-ui.js
  apis-demo.js        # задание 9
  chart-arccos.js     # задание 10
  scroll-statues.js   # задание 11
```

**Подключение скриптов:** `{% block extra_js %}` в шаблонах; Chart.js — CDN на странице «Задания JS».

---

## Docker

```bash
docker-compose up --build
```

Подробнее — в `DEPLOY.md`.
