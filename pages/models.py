"""
Модели общих страниц: главная, о компании, новости, словарь, контакты,
вакансии, отзывы, промокоды, партнёры. Обязательные таблицы по заданию.
"""
from django.db import models
from django.conf import settings


class Article(models.Model):
    """Статья для главной страницы (последняя опубликованная)."""
    title = models.CharField('Заголовок', max_length=300)
    content = models.TextField('Содержание')
    is_published = models.BooleanField('Опубликовано', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Изменено', auto_now=True)

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Partner(models.Model):
    """Компании-партнёры: логотип и ссылка на сайт."""
    name = models.CharField('Название', max_length=200)
    logo = models.FileField('Логотип', upload_to='partners/', null=True, blank=True)
    website_url = models.URLField('Сайт')
    order = models.PositiveSmallIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)

    class Meta:
        verbose_name = 'Партнёр'
        verbose_name_plural = 'Партнёры'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class CompanyInfo(models.Model):
    """О компании: текстовые блоки (таблица в БД)."""
    title = models.CharField('Заголовок', max_length=200)
    content = models.TextField('Текст')
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Блок о компании'
        verbose_name_plural = 'О компании'
        ordering = ['order']

    def __str__(self):
        return self.title


class CompanyProfile(models.Model):
    """
    Профиль компании: логотип, видео, аудио, реквизиты, сертификат.
    Обычно одна запись.
    """
    name = models.CharField('Название организации', max_length=300, default='Музей искусств')
    logo = models.FileField('Логотип', upload_to='company/', null=True, blank=True)
    video_file = models.FileField('Видео', upload_to='company/video/', null=True, blank=True)
    video_url = models.URLField('URL видео (iframe)', blank=True)
    audio_file = models.FileField('Аудиогид / аудио', upload_to='company/audio/', null=True, blank=True)
    requisites = models.TextField('Реквизиты', blank=True)
    certificate_text = models.TextField('Сертификат (текст без стилей)', blank=True)
    map_embed_url = models.URLField(
        'URL карты (iframe)',
        blank=True,
        default='https://www.openstreetmap.org/export/embed.html?bbox=27.55%2C53.89%2C27.57%2C53.91&layer=mapnik',
    )

    class Meta:
        verbose_name = 'Профиль компании'
        verbose_name_plural = 'Профиль компании'

    def __str__(self):
        return self.name


class CompanyHistory(models.Model):
    """История компании по годам."""
    year = models.PositiveIntegerField('Год')
    title = models.CharField('Событие', max_length=300)
    description = models.TextField('Описание', blank=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Историческое событие'
        verbose_name_plural = 'История по годам'
        ordering = ['year', 'order']

    def __str__(self):
        return f'{self.year}: {self.title}'


class News(models.Model):
    """Новости: заголовок, краткое содержание (одно предложение), картинка."""
    title = models.CharField('Заголовок', max_length=300)
    summary = models.CharField('Краткое содержание', max_length=500)
    content = models.TextField('Полный текст', blank=True)
    image = models.FileField('Картинка', upload_to='news/', null=True, blank=True)
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)
    updated_at = models.DateTimeField('Изменено', auto_now=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class FAQ(models.Model):
    """Словарь терминов / часто задаваемые вопросы с датой добавления."""
    question = models.CharField('Вопрос / термин', max_length=500)
    answer = models.TextField('Ответ / определение')
    added_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Вопрос-ответ'
        verbose_name_plural = 'Словарь терминов (FAQ)'
        ordering = ['-added_at']

    def __str__(self):
        return self.question[:80]


class Contact(models.Model):
    """Контакты: фото сотрудника, описание, телефон, почта."""
    name = models.CharField('ФИО', max_length=200)
    role = models.CharField('Должность / выполняемые работы', max_length=300)
    photo = models.FileField('Фото', upload_to='contacts/', null=True, blank=True)
    phone = models.CharField('Телефон', max_length=25, blank=True)
    email = models.EmailField('Email', blank=True)
    description = models.TextField('Описание', blank=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'
        ordering = ['order']

    def __str__(self):
        return self.name

    def clean(self):
        from museum.models import validate_phone
        super().clean()
        if self.phone:
            validate_phone(self.phone)


class Vacancy(models.Model):
    """Вакансии с описанием."""
    title = models.CharField('Название', max_length=300)
    description = models.TextField('Описание')
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Изменено', auto_now=True)

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Review(models.Model):
    """Отзывы: имя, оценка, текст, дата. Связь с User для залогиненных."""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews',
    )
    author_name = models.CharField('Имя', max_length=200)
    rating = models.PositiveSmallIntegerField('Оценка', choices=RATING_CHOICES)
    text = models.TextField('Текст отзыва')
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author_name} — {self.rating}'


class PromoCode(models.Model):
    """Промокоды и купоны: действующие и в архиве."""
    code = models.CharField('Код', max_length=50, unique=True)
    description = models.CharField('Описание', max_length=300, blank=True)
    discount_percent = models.DecimalField(
        'Скидка %',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    discount_amount = models.DecimalField(
        'Скидка (фикс.)',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField('Действующий', default=True)
    valid_from = models.DateTimeField('Действует с', null=True, blank=True)
    valid_until = models.DateTimeField('Действует до', null=True, blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Промокод / купон'
        verbose_name_plural = 'Промокоды и купоны'
        ordering = ['-is_active', '-created_at']

    def __str__(self):
        return f'{self.code} ({"активен" if self.is_active else "архив"})'
