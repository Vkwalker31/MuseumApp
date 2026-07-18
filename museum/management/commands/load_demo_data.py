"""
Команда для наполнения БД демо-данными (не менее 10 экспонатов и др.).
Запуск: python manage.py load_demo_data
"""
import logging
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from museum.models import (
    ArtType,
    Hall,
    EmployeePosition,
    Employee,
    Exhibit,
    Tour,
    TicketPrice,
    SEASON_CHOICES,
)
from pages.models import Article, News, FAQ, Contact, Vacancy, Review, PromoCode, CompanyInfo

User = get_user_model()
logger = logging.getLogger('museum')


class Command(BaseCommand):
    help = 'Load demo data: 10+ exhibits, halls, employees, etc.'

    def handle(self, *args, **options):
        # Виды искусства
        at1, _ = ArtType.objects.get_or_create(name='Живопись')
        at2, _ = ArtType.objects.get_or_create(name='Скульптура')
        at3, _ = ArtType.objects.get_or_create(name='Графика')
        at4, _ = ArtType.objects.get_or_create(name='Декоративно-прикладное')
        # Залы
        h1, _ = Hall.objects.get_or_create(number='1', defaults={'name': 'Зал древнего искусства', 'floor': 1, 'area': Decimal('120.5')})
        h2, _ = Hall.objects.get_or_create(number='2', defaults={'name': 'Зал живописи', 'floor': 1, 'area': Decimal('200')})
        h3, _ = Hall.objects.get_or_create(number='3', defaults={'name': 'Зал скульптуры', 'floor': 2, 'area': Decimal('180')})
        # Должности
        pos1, _ = EmployeePosition.objects.get_or_create(name='Хранитель')
        pos2, _ = EmployeePosition.objects.get_or_create(name='Экскурсовод')
        # Сотрудник без user (для демо)
        emp1, _ = Employee.objects.get_or_create(
            full_name='Иванов Иван Иванович',
            defaults={'hall': h1, 'position': pos1, 'phone': '+375 (29) 123-45-67', 'birth_date': date(1990, 5, 15)}
        )
        emp2, _ = Employee.objects.get_or_create(
            full_name='Петрова Мария Сергеевна',
            defaults={'hall': h2, 'position': pos2, 'phone': '+375 (33) 111-22-33', 'birth_date': date(1985, 8, 20)}
        )
        # Экспонаты (10+)
        exhibits_data = [
            ('Картина «Утро в лесу»', at1, h2, emp2),
            ('Скульптура «Мыслитель»', at2, h3, emp1),
            ('Гравюра «Вид города»', at3, h2, emp2),
            ('Ваза керамическая', at4, h1, emp1),
            ('Портрет неизвестного', at1, h2, emp2),
            ('Бюст поэта', at2, h3, emp1),
            ('Эскиз к фреске', at3, h2, emp2),
            ('Подсвечник бронзовый', at4, h1, emp1),
            ('Пейзаж «Осень»', at1, h2, emp2),
            ('Статуя «Ника»', at2, h3, emp1),
            ('Акварель «Море»', at3, h2, emp2),
            ('Ковёр ручной работы', at4, h1, emp1),
        ]
        base_date = date(2023, 1, 1)
        for i, (name, art_type, hall, guardian) in enumerate(exhibits_data):
            Exhibit.objects.get_or_create(
                name=name,
                defaults={
                    'art_type': art_type,
                    'hall': hall,
                    'guardian': guardian,
                    'date_of_entry': base_date + timedelta(days=i * 30),
                    'description': f'Описание экспоната: {name}.',
                }
            )
        # Экскурсии по сезонам
        now = timezone.now()
        for season_code, _ in SEASON_CHOICES:
            Tour.objects.get_or_create(
                code=f'EX-{season_code.upper()}-001',
                defaults={
                    'name': f'Обзорная экскурсия ({season_code})',
                    'date': now - timedelta(days=100),
                    'group_size': 15,
                    'conductor': emp2,
                    'season': season_code,
                }
            )
        # Страницы
        Article.objects.get_or_create(title='Добро пожаловать в музей', defaults={'content': 'Краткая информация о последней статье. Музей приглашает посетителей.', 'is_published': True})
        CompanyInfo.objects.get_or_create(title='О нас', defaults={'content': 'Текст о компании.', 'order': 0})
        for i in range(3):
            News.objects.get_or_create(
                title=f'Новость {i+1}',
                defaults={'summary': f'Краткое содержание новости {i+1}.', 'content': f'Полный текст новости {i+1}.'}
            )
        FAQ.objects.get_or_create(question='Что такое экспозиция?', defaults={'answer': 'Экспозиция — выставленные для обзора экспонаты.'})
        Contact.objects.get_or_create(name='Приёмная', defaults={'role': 'Общие вопросы', 'phone': '+375 (29) 200-00-00', 'order': 0})
        Vacancy.objects.get_or_create(title='Экскурсовод', defaults={'description': 'Проведение экскурсий.', 'is_active': True})
        PromoCode.objects.get_or_create(code='WELCOME10', defaults={'description': 'Скидка 10%', 'discount_percent': Decimal('10'), 'is_active': True})
        PromoCode.objects.get_or_create(code='OLD5', defaults={'description': 'Архивный купон', 'discount_percent': Decimal('5'), 'is_active': False})
        TicketPrice.objects.get_or_create(name='Взрослый будни', defaults={'base_price': Decimal('15.00'), 'day_of_week': 0, 'is_adult': True})
        TicketPrice.objects.get_or_create(name='Взрослый выходные', defaults={'base_price': Decimal('20.00'), 'day_of_week': 5, 'is_adult': True})
        TicketPrice.objects.get_or_create(name='Детский', defaults={'base_price': Decimal('8.00'), 'is_child': True, 'is_adult': False})
        TicketPrice.objects.get_or_create(name='Аудиогид', defaults={'base_price': Decimal('5.00'), 'is_extra_service': True})
        self.stdout.write(self.style.SUCCESS('Demo data loaded. Exhibits: %s' % Exhibit.objects.count()))
        logger.info('Demo data loaded. Exhibits: %s', Exhibit.objects.count())
