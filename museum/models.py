"""
Модели предметной области Музей: залы, экспонаты, сотрудники, экскурсии, билеты.
Связи: OneToOne (профиль пользователя), ForeignKey, ManyToMany.
"""
import re
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_phone(value):
    """Формат +375 (29) XXX-XX-XX (или другие коды 25, 33, 44)."""
    if not value:
        return
    pattern = r'^\+375\s?\((25|29|33|44)\)\s?\d{3}-\d{2}-\d{2}$'
    if not re.match(pattern, re.sub(r'\s+', ' ', value.strip())):
        raise ValidationError(
            'Введите номер в формате +375 (29) XXX-XX-XX',
            code='invalid_phone',
        )


def validate_age_18(birth_date):
    """Сотрудники и клиенты должны быть 18+."""
    if not birth_date:
        return
    today = timezone.localdate()
    age = (today - birth_date).days // 365
    if age < 18:
        raise ValidationError(
            'Возраст должен быть не менее 18 лет.',
            code='age_restriction',
        )


class ArtType(models.Model):
    """Вид искусства."""
    name = models.CharField('Наименование', max_length=200)

    class Meta:
        verbose_name = 'Вид искусства'
        verbose_name_plural = 'Виды искусства'
        ordering = ['name']

    def __str__(self):
        return self.name


class Hall(models.Model):
    """Зал музея: номер, название, этаж, площадь."""
    number = models.CharField('Номер зала', max_length=20)
    name = models.CharField('Название', max_length=200)
    floor = models.PositiveSmallIntegerField('Этаж')
    area = models.DecimalField(
        'Площадь (м²)',
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Зал'
        verbose_name_plural = 'Залы'
        ordering = ['floor', 'number']

    def __str__(self):
        return f'{self.number} — {self.name}'


class EmployeePosition(models.Model):
    """Должность сотрудника."""
    name = models.CharField('Наименование', max_length=200)

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности сотрудников'
        ordering = ['name']

    def __str__(self):
        return self.name


class Employee(models.Model):
    """
    Сотрудник музея. Связь с User — OneToOne (профиль).
    Возраст 18+, телефон в формате +375 (29) XXX-XX-XX.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='employee_profile',
    )
    full_name = models.CharField('ФИО', max_length=200)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    hall = models.ForeignKey(
        Hall,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name='Зал',
    )
    phone = models.CharField(
        'Телефон',
        max_length=25,
        validators=[validate_phone],
        blank=True,
    )
    position = models.ForeignKey(
        EmployeePosition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name='Должность',
    )
    email = models.EmailField('Email', blank=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['full_name']

    def __str__(self):
        return self.full_name

    def clean(self):
        super().clean()
        if self.birth_date:
            validate_age_18(self.birth_date)


class Visitor(models.Model):
    """
    Посетитель (клиент) музея. OneToOne с User.
    Возраст 18+, телефон в формате +375 (29) XXX-XX-XX.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='visitor_profile',
    )
    full_name = models.CharField('ФИО', max_length=200)
    birth_date = models.DateField('Дата рождения')
    phone = models.CharField(
        'Телефон',
        max_length=25,
        validators=[validate_phone],
    )
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Изменено', auto_now=True)

    class Meta:
        verbose_name = 'Посетитель'
        verbose_name_plural = 'Посетители'
        ordering = ['full_name']

    def __str__(self):
        return self.full_name

    def clean(self):
        super().clean()
        if self.birth_date:
            validate_age_18(self.birth_date)

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = timezone.localdate()
        return (today - self.birth_date).days // 365


class Exhibit(models.Model):
    """
    Экспонат: название, вид искусства, дата поступления, зал, ответственный (хранитель).
    """
    name = models.CharField('Название', max_length=300)
    art_type = models.ForeignKey(
        ArtType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exhibits',
        verbose_name='Вид искусства',
    )
    date_of_entry = models.DateField('Дата поступления', null=True, blank=True)
    hall = models.ForeignKey(
        Hall,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exhibits',
        verbose_name='Зал',
    )
    guardian = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='guarded_exhibits',
        verbose_name='Ответственный (хранитель)',
    )
    description = models.TextField('Описание', blank=True)
    inventory_number = models.CharField('Инвентарный номер', max_length=50, blank=True)
    dating = models.CharField('Датировка', max_length=100, blank=True)
    image = models.FileField('Фото', upload_to='exhibits/', null=True, blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Изменено', auto_now=True)

    class Meta:
        verbose_name = 'Экспонат'
        verbose_name_plural = 'Экспонаты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Exhibition(models.Model):
    """Экспозиция — может объединять несколько экспонатов (ManyToMany)."""
    name = models.CharField('Название', max_length=300)
    description = models.TextField('Описание', blank=True)
    hall = models.ForeignKey(
        Hall,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exhibitions',
        verbose_name='Зал',
    )
    exhibits = models.ManyToManyField(
        Exhibit,
        through='ExhibitionExhibit',
        related_name='exhibitions',
        blank=True,
        verbose_name='Экспонаты',
    )
    start_date = models.DateField('Дата начала', null=True, blank=True)
    end_date = models.DateField('Дата окончания', null=True, blank=True)

    class Meta:
        verbose_name = 'Экспозиция'
        verbose_name_plural = 'Экспозиции'
        ordering = ['name']

    def __str__(self):
        return self.name


class ExhibitionExhibit(models.Model):
    """Промежуточная модель для связи Экспозиция — Экспонаты (с доп. полями при необходимости)."""
    exhibition = models.ForeignKey(Exhibition, on_delete=models.CASCADE)
    exhibit = models.ForeignKey(Exhibit, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['order']


class Show(models.Model):
    """Выставка / мероприятие."""
    name = models.CharField('Название', max_length=300)
    description = models.TextField('Описание', blank=True)
    start_date = models.DateField('Дата начала', null=True, blank=True)
    end_date = models.DateField('Дата окончания', null=True, blank=True)
    exhibits = models.ManyToManyField(
        Exhibit,
        related_name='shows',
        blank=True,
        verbose_name='Экспонаты',
    )

    class Meta:
        verbose_name = 'Выставка'
        verbose_name_plural = 'Выставки'
        ordering = ['-start_date']

    def __str__(self):
        return self.name


SEASON_CHOICES = [
    ('winter', 'Зима'),
    ('spring', 'Весна'),
    ('summer', 'Лето'),
    ('autumn', 'Осень'),
]


class Tour(models.Model):
    """
    Экскурсия: код, наименование, дата, количество человек в группе, проводник.
    Учёт по сезонам для статистики.
    """
    code = models.CharField('Код экскурсии', max_length=50)
    name = models.CharField('Наименование', max_length=300)
    date = models.DateTimeField('Дата и время проведения')
    group_size = models.PositiveIntegerField('Количество человек в группе', default=0)
    conductor = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tours',
        verbose_name='Проводник',
    )
    season = models.CharField(
        'Сезон',
        max_length=10,
        choices=SEASON_CHOICES,
        blank=True,
    )
    duration_minutes = models.PositiveSmallIntegerField(
        'Длительность (мин.)',
        default=60,
    )
    audience = models.CharField('Целевая аудитория', max_length=200, blank=True)
    price = models.DecimalField(
        'Стоимость (BYN)',
        max_digits=8,
        decimal_places=2,
        default=0,
    )
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Изменено', auto_now=True)

    class Meta:
        verbose_name = 'Экскурсия'
        verbose_name_plural = 'Экскурсии'
        ordering = ['-date']

    def __str__(self):
        return f'{self.code} — {self.name}'


class TicketPrice(models.Model):
    """
    Услуга / тариф посещения (каталог товаров): цена, описание, изображение.
    Зависит от дня недели, возраста, доп. услуг.
    """
    name = models.CharField('Наименование тарифа', max_length=200)
    base_price = models.DecimalField('Базовая цена', max_digits=10, decimal_places=2, default=0)
    description = models.TextField('Описание услуги', blank=True)
    image = models.FileField('Изображение', upload_to='services/', null=True, blank=True)
    # 0-6 понедельник-воскресенье, null — любой день
    day_of_week = models.PositiveSmallIntegerField(
        'День недели (0-6, пусто — любой)',
        null=True,
        blank=True,
    )
    is_child = models.BooleanField('Детский', default=False)
    is_adult = models.BooleanField('Взрослый', default=True)
    is_extra_service = models.BooleanField('Доп. услуга', default=False)

    class Meta:
        verbose_name = 'Тариф / услуга'
        verbose_name_plural = 'Тарифы / услуги'
        ordering = ['name']

    def __str__(self):
        return self.name


class TicketPurchase(models.Model):
    """Покупка билета (для зарегистрированного посетителя)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ticket_purchases',
    )
    tour = models.ForeignKey(
        Tour,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ticket_purchases',
    )
    price = models.DecimalField('Сумма', max_digits=10, decimal_places=2, default=0)
    promo_code = models.CharField('Промокод', max_length=50, blank=True)
    purchased_at = models.DateTimeField('Дата покупки', auto_now_add=True)

    class Meta:
        verbose_name = 'Покупка билета'
        verbose_name_plural = 'Покупки билетов'
        ordering = ['-purchased_at']

    def __str__(self):
        return f'Билет #{self.id} — {self.user}'
