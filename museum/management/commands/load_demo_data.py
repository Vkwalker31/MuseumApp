"""
Команда для наполнения БД демо-данными (не менее 10 экспонатов и данные для ЛР1).
Запуск: python manage.py load_demo_data
"""
import logging
from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.files import File
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
    Exhibition,
    Show,
    SEASON_CHOICES,
)
from pages.models import (
    Article,
    News,
    FAQ,
    Contact,
    Vacancy,
    Review,
    PromoCode,
    CompanyInfo,
    Partner,
    CompanyProfile,
    CompanyHistory,
)

User = get_user_model()
logger = logging.getLogger('museum')

DOWNLOAD_USER_AGENT = 'MuseumApp-DemoData/1.0 (Educational; +https://museum.local)'

# Реалистичные фото: Unsplash (портреты, новости) и Wikimedia Commons (экспонаты).
REMOTE_PHOTO_URLS = {
    'contacts/male_admin.png': (
        'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=320&q=80'
    ),
    'contacts/female_guide.png': (
        'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=320&q=80'
    ),
    'contacts/female_reception.png': (
        'https://images.unsplash.com/photo-1551836022-deb4988cc6c0?w=320&q=80'
    ),
    'contacts/female_keeper.png': (
        'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=320&q=80'
    ),
    'contacts/male_security.png': (
        'https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=320&q=80'
    ),
    'news/news_night_tour.png': (
        'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=640&q=80'
    ),
    'news/news_restoration.png': (
        'https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?w=640&q=80'
    ),
    'news/news_workshop.png': (
        'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=640&q=80'
    ),
    'news/news_exhibition.png': (
        'https://images.unsplash.com/photo-1743119631789-787bd3ca9e9e?w=640&q=80'
    ),
    'news/news_lecture.png': (
        'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=640&q=80'
    ),
    'news/news_festival.png': (
        'https://images.unsplash.com/photo-1564399579883-451a5d44ec08?w=640&q=80'
    ),
    'news/news_catalog.png': (
        'https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=640&q=80'
    ),
    'exhibits/exhibit_01.png': (
        'https://commons.wikimedia.org/wiki/Special:FilePath/'
        'Shishkin%2C_Ivan_-_Morning_in_a_Pine_Forest.jpg?width=640'
    ),
    'exhibits/exhibit_02.png': (
        'https://commons.wikimedia.org/wiki/Special:FilePath/'
        'The_Thinker%2C_Rodin.jpg?width=480'
    ),
    'exhibits/exhibit_03.png': (
        'https://commons.wikimedia.org/wiki/Special:FilePath/'
        'The_Four_Horsemen_%28CBL_WEp_0021%29.jpg?width=640'
    ),
    'exhibits/exhibit_04.png': (
        'https://commons.wikimedia.org/wiki/Special:FilePath/'
        'Terracotta_amphora_%28jar%29_MET_DT272.jpg?width=480'
    ),
    'exhibits/exhibit_05.png': (
        'https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=480&q=80'
    ),
    'exhibits/exhibit_06.png': (
        'https://images.unsplash.com/photo-1763734546247-83a8792bf0eb?w=480&q=80'
    ),
    'exhibits/exhibit_07.png': (
        'https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=480&q=80'
    ),
    'exhibits/exhibit_08.png': (
        'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=480&q=80'
    ),
    'exhibits/exhibit_09.png': (
        'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=640&q=80'
    ),
    'exhibits/exhibit_10.png': (
        'https://commons.wikimedia.org/wiki/Special:FilePath/'
        'Winged_Victory_of_Samothrace.jpg?width=480'
    ),
    'exhibits/exhibit_11.png': (
        'https://images.unsplash.com/photo-1505142468610-359e7d316be0?w=640&q=80'
    ),
    'exhibits/exhibit_12.png': (
        'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=640&q=80'
    ),
}

CERTIFICATE_TEXT = """СЕРТИФИКАТ АККРЕДИТАЦИИ В ЕДИНОМ РЕЕСТРЕ МУЗЕЙНЫХ ОРГАНИЗАЦИЙ РЕСПУБЛИКИ БЕЛАРУСЬ

РЕЕСТР МУЗЕЙНЫХ ОРГАНИЗАЦИЙ

СЕРТИФИКАТ об аккредитации музея

г. Минск                                                    15 марта 2024 г.

Государственное учреждение культуры «Музей искусств»
УНП 100000000
Реестровый номер: МИ-2024-001

Ковалёва Е.В., Директор Музея искусств

Министерство культуры Республики Беларусь
220030, г. Минск, ул. Культуры, 1
+375 (17) 200-00-00
info@museum.by"""


class Command(BaseCommand):
    help = 'Load demo data: exhibits, pages, partners, company profile, services.'

    def _ensure_static_images(self, static_dir):
        """Логотип, баннеры, логотипы партнёров, favicon."""
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            self.stdout.write(self.style.WARNING('Pillow не установлен — статические картинки не созданы.'))
            return

        images = static_dir / 'images'
        banners_dir = images / 'banners'
        partners_dir = images / 'partners'
        banners_dir.mkdir(parents=True, exist_ok=True)
        partners_dir.mkdir(parents=True, exist_ok=True)

        def banner(name, color, text):
            path = banners_dir / name
            if path.exists():
                return
            img = Image.new('RGB', (1200, 320), color)
            d = ImageDraw.Draw(img)
            d.rectangle([20, 20, 1180, 300], outline=(255, 255, 255), width=3)
            d.text((48, 130), text, fill=(255, 255, 255))
            img.save(path)

        banner('banner1.png', (45, 55, 95), 'Vystavka mesyaca')
        banner('banner2.png', (80, 60, 40), 'Ekskursii po zalam')
        banner('banner3.png', (50, 90, 70), 'Semejnyj bilet')

        logo_path = images / 'logo.png'
        if not logo_path.exists():
            img = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            d.ellipse([8, 8, 88, 88], fill=(44, 62, 107))
            d.ellipse([20, 20, 76, 76], fill=(201, 162, 39))
            d.text((28, 38), 'MI', fill=(255, 255, 255))
            img.save(logo_path)

        for fname, color, letter in [
            ('partner_hermitage.png', (60, 80, 120), 'E'),
            ('partner_tretyakov.png', (120, 60, 40), 'T'),
            ('partner_louvre.png', (40, 80, 100), 'L'),
        ]:
            path = partners_dir / fname
            if not path.exists():
                img = Image.new('RGB', (120, 120), color)
                d = ImageDraw.Draw(img)
                d.ellipse([10, 10, 110, 110], outline=(255, 255, 255), width=3)
                d.text((45, 45), letter, fill=(255, 255, 255))
                img.save(path)

        favicon_path = static_dir / 'favicon.ico'
        if not favicon_path.exists():
            icon = Image.new('RGB', (32, 32), (44, 62, 107))
            d = ImageDraw.Draw(icon)
            d.ellipse([4, 4, 28, 28], fill=(201, 162, 39))
            icon.save(favicon_path, format='ICO', sizes=[(32, 32)])

        gallery_dir = images / 'gallery'
        gallery_dir.mkdir(parents=True, exist_ok=True)
        gallery_specs = [
            ('painting1.png', (90, 60, 40), 'Forest'),
            ('painting2.png', (60, 80, 110), 'Sea'),
            ('painting3.png', (110, 70, 90), 'Portrait'),
            ('painting4.png', (70, 100, 80), 'Still life'),
        ]
        for filename, color, label in gallery_specs:
            path = gallery_dir / filename
            if not path.exists():
                img = Image.new('RGB', (220, 290), color)
                d = ImageDraw.Draw(img)
                d.rectangle([12, 12, 208, 278], outline=(212, 175, 55), width=2)
                d.text((24, 130), label, fill=(255, 255, 255))
                img.save(path)

    def _ensure_service_images(self, media_dir):
        """Картинки услуг для каталога."""
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            return

        services_dir = media_dir / 'services'
        services_dir.mkdir(parents=True, exist_ok=True)
        specs = [
            ('adult.png', (44, 62, 107), 'Vzroslyj'),
            ('weekend.png', (90, 60, 50), 'Vyhodnye'),
            ('child.png', (70, 120, 90), 'Detskij'),
            ('audio.png', (100, 80, 140), 'Audiogid'),
        ]
        for filename, color, label in specs:
            path = services_dir / filename
            if not path.exists():
                img = Image.new('RGB', (320, 200), color)
                d = ImageDraw.Draw(img)
                d.rectangle([12, 12, 308, 188], outline=(255, 255, 255), width=2)
                d.text((24, 88), label, fill=(255, 255, 255))
                img.save(path)

    def _download_photo(self, media_dir, rel_path, force=True):
        """Скачать фото по URL и сохранить как PNG в media/."""
        import time

        url = REMOTE_PHOTO_URLS.get(rel_path)
        if not url:
            return None
        dest = media_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and not force:
            return dest
        try:
            time.sleep(0.4)
            req = Request(url, headers={'User-Agent': DOWNLOAD_USER_AGENT})
            with urlopen(req, timeout=60) as response:
                raw = response.read()
            try:
                from PIL import Image
                img = Image.open(BytesIO(raw))
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                max_side = 640 if 'exhibits/' in rel_path or 'news/' in rel_path else 320
                if max(img.size) > max_side:
                    img.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
                img.save(dest, format='PNG', optimize=True)
            except Exception:
                dest.write_bytes(raw)
            return dest
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f'Не удалось загрузить {rel_path}: {exc}'))
            return None

    def _ensure_real_photos(self, media_dir, force=True):
        """Загрузить все демо-фото (новости, экспонаты, контакты) из интернета."""
        paths = {}
        for rel_path in REMOTE_PHOTO_URLS:
            downloaded = self._download_photo(media_dir, rel_path, force=force)
            if downloaded:
                paths[rel_path] = downloaded
        return paths

    def _news_content(self, title):
        """Развёрнутый текст новости (4 абзаца)."""
        bodies = {
            'Ночная экскурсия по залам': (
                'В субботу музей открывает двери после заката для особой программы «Ночь в залах». '
                'Посетители смогут пройти по маршруту с фонарями и услышать истории, которые обычно не звучат на дневных экскурсиях.\n\n'
                'Маршрут начинается в зале древнего искусства и завершается у временной выставки современных авторов. '
                'Кураторы подготовили короткие комментарии к ключевым экспонатам и покажут, как меняется восприятие картины при разном освещении.\n\n'
                'Для участников предусмотрены остановки у витрин с редкими монетами и гравюрами. '
                'Экскурсоводы расскажут о правилах хранения и о том, как музейные специалисты готовят предметы к показу.\n\n'
                'Количество мест ограничено. Запись открыта на стойке информации и через личный кабинет на сайте.'
            ),
            'Реставрация «Утра в лесу»': (
                'Хранители завершили консервацию знаменитого пейзажа «Утро в лесу» — одного из самых узнаваемых полотен постоянной экспозиции. '
                'Работы велись в специально оборудованной мастерской при закрытом доступе посетителей.\n\n'
                'Специалисты провели очистку лакового слоя, укрепили красочный слой и устранили мелкие деформации холста. '
                'Каждый этап фиксировался в журнале реставрации с фотофиксацией.\n\n'
                'После возвращения картины в зал живописи посетители увидят обновлённую подсветку и новую этикетку с историей поступления экспоната в фонд.\n\n'
                'Кураторский текст к полотну дополнен материалами о технике живописи и о том, как музей определяет приоритеты реставрационных работ.'
            ),
            'Детская мастерская': (
                'Юные посетители создадут открытки по мотивам экспонатов в рамках воскресной программы «Мастерская у витрины». '
                'Занятие рассчитано на детей от 7 до 12 лет в сопровождении взрослых.\n\n'
                'Педагоги музея покажут, как художники передают текстуру дерева, металла и ткани, а затем предложат повторить приёмы на простых материалах.\n\n'
                'В программе — короткая экскурсия по залу декоративно-прикладного искусства и работа с шаблонами орнаментов из коллекции музея.\n\n'
                'Участие бесплатное при предъявлении входного билета. Регистрация обязательна: количество мест в мастерской ограничено.'
            ),
            'Новая временная выставка': (
                'Открывается экспозиция белорусских художников XX века в специально подготовленном зале второго этажа. '
                'На выставке представлены живопись, графика и эскизы из фондов музея и частных коллекций.\n\n'
                'Экспозиция показывает, как менялся художественный язык от послевоенного модернизма до позднего социалистического реализма и авторских поисков 1980-х годов.\n\n'
                'Для каждого раздела подготовлены тексты кураторов и аудиокомментарии. В центре зала — интерактивная витрина с редкими альбомами и письмами художников.\n\n'
                'Выставка продлится три месяца. В дни открытия пройдут лекции и встречи с исследователями искусства.'
            ),
            'Лекция о символизме': (
                'Куратор расскажет о скрытых смыслах полотен конца XIX века в рамках цикла «Читая картину». '
                'Лекция сопровождается демонстрацией репродукций и фрагментов из архива музея.\n\n'
                'Слушатели узнают, как символы природы, архитектуры и бытовых предметов помогают понять замысел художника и контекст эпохи.\n\n'
                'После выступления гостей пригласят к обсуждению и короткому осмотру связанных экспонатов в зале живописи.\n\n'
                'Вход по билету музея. Начало в 18:00, продолжительность — 90 минут.'
            ),
            'Фестиваль «Ночь музеев»': (
                'Особая программа с концертами и мастер-классами до полуночи пройдёт в рамках общегородского фестиваля «Ночь музеев».\n\n'
                'Посетители смогут посетить все постоянные залы, принять участие в викторине и посмотреть выступление камерного ансамбля в атrium музея.\n\n'
                'Для семей с детьми подготовлен квест по следам экспонатов, а для взрослых — кураторские мини-экскурсии каждые 30 минут.\n\n'
                'Билеты рекомендуется приобретать заранее. Подробное расписание опубликовано на главной странице сайта.'
            ),
            'Цифровой каталог фонда': (
                'Часть коллекции доступна для онлайн-просмотра на сайте музея: опубликованы описания, фотографии и история поступления отобранных экспонатов.\n\n'
                'Цифровой каталог создан для исследователей, студентов и всех, кто интересуется историей искусства, но не может посетить музей лично.\n\n'
                'К каждой записи приложены данные об инвентарном номере, датировке и ответственном хранителе. Планируется регулярное пополнение раздела.\n\n'
                'Музей продолжит оцифровку фонда и приглашает волонтёров-переводчиков для подготовки англоязычных описаний.'
            ),
        }
        return bodies.get(title, 'Подробности уточняйте в пресс-службе музея.')

    def handle(self, *args, **options):
        static = Path(settings.BASE_DIR) / 'static'
        media = Path(settings.MEDIA_ROOT)

        self._ensure_static_images(static)
        self._ensure_service_images(media)
        photo_paths = self._ensure_real_photos(media, force=True)
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
        emp1, _ = Employee.objects.get_or_create(
            full_name='Иванов Иван Иванович',
            defaults={'hall': h1, 'position': pos1, 'phone': '+375 (29) 123-45-67', 'birth_date': date(1990, 5, 15), 'email': 'ivanov@museum.by'}
        )
        emp2, _ = Employee.objects.get_or_create(
            full_name='Петрова Мария Сергеевна',
            defaults={'hall': h2, 'position': pos2, 'phone': '+375 (33) 111-22-33', 'birth_date': date(1985, 8, 20), 'email': 'petrova@museum.by'}
        )
        exhibits_data = [
            ('Картина «Утро в лесу»', at1, h2, emp2, 'ЖИ-0001', 'XIX век', 'Пейзаж с утренним лесом; центральный экспонат зала живописи.'),
            ('Скульптура «Мыслитель»', at2, h3, emp1, 'СК-0002', '1905 г.', 'Бронзовая скульптура в классической манере.'),
            ('Гравюра «Вид города»', at3, h2, emp2, 'ГР-0003', '1880-е гг.', 'Гравюра на меди с видом исторического центра.'),
            ('Ваза керамическая', at4, h1, emp1, 'ДП-0004', 'XVIII век', 'Керамическая ваза с растительным орнаментом.'),
            ('Портрет неизвестного', at1, h2, emp2, 'ЖИ-0005', '1820-е гг.', 'Круглый портрет неизвестного дворянина.'),
            ('Бюст поэта', at2, h3, emp1, 'СК-0006', '1910 г.', 'Мраморный бюст белорусского поэта.'),
            ('Эскиз к фреске', at3, h2, emp2, 'ГР-0007', '1930-е гг.', 'Подготовительный эскиз монументальной росписи.'),
            ('Подсвечник бронзовый', at4, h1, emp1, 'ДП-0008', 'XIX век', 'Бронзовый подсвечник церковного обихода.'),
            ('Пейзаж «Осень»', at1, h2, emp2, 'ЖИ-0009', '1895 г.', 'Пейзаж с золотой листвой и рекой.'),
            ('Статуя «Ника»', at2, h3, emp1, 'СК-0010', 'Копия, XX век', 'Уменьшенная копия античной скульптуры.'),
            ('Акварель «Море»', at3, h2, emp2, 'ГР-0011', '1920-е гг.', 'Морской пейзаж акварелью на бумаге.'),
            ('Ковёр ручной работы', at4, h1, emp1, 'ДП-0012', 'XIX век', 'Ковёр с геометрическим орнаментом.'),
        ]
        exhibit_image_paths = {
            i: photo_paths.get(f'exhibits/exhibit_{i:02d}.png')
            for i in range(1, 13)
        }
        base_date = date(2023, 1, 1)
        for i, (name, art_type, hall, guardian, inv, dating, desc) in enumerate(exhibits_data):
            ex, _ = Exhibit.objects.get_or_create(
                name=name,
                defaults={
                    'art_type': art_type,
                    'hall': hall,
                    'guardian': guardian,
                    'date_of_entry': base_date + timedelta(days=i * 30),
                    'inventory_number': inv,
                    'dating': dating,
                    'description': desc,
                },
            )
            updated = False
            if not ex.inventory_number:
                ex.inventory_number = inv
                updated = True
            if not ex.dating:
                ex.dating = dating
                updated = True
            if ex.description != desc:
                ex.description = desc
                updated = True
            if updated:
                ex.save()
            img_path = exhibit_image_paths.get(i + 1)
            if img_path and img_path.exists():
                with img_path.open('rb') as f:
                    ex.image.save(f'exhibit_{i + 1:02d}.png', File(f), save=True)

        now = timezone.now()
        tours_data = [
            ('EX-MAIN-001', 'Обзорная экскурсия по главному корпусу', 'summer', 90, 'Все возрасты', Decimal('12.00'), 18, 30),
            ('EX-NIGHT-002', 'Ночь в музее: Тайны запасников', 'winter', 120, 'Взрослые 16+', Decimal('18.00'), 12, 120),
            ('EX-QUEST-003', 'Интерактивный квест для школьников', 'spring', 75, 'Школьники 10–14 лет', Decimal('8.00'), 22, 75),
            ('EX-CUR-004', 'Кураторская экскурсия по выставке XIX века', 'autumn', 100, 'Любители искусства', Decimal('15.00'), 10, 100),
            ('EX-FAM-005', 'Семейная программа «Загадки витрин»', 'summer', 60, 'Семьи с детьми', Decimal('10.00'), 20, 60),
            ('EX-ART-006', 'Мастер-класс по гравюре', 'spring', 80, 'Подростки и взрослые', Decimal('14.00'), 8, 80),
        ]
        for j, (code, name, season, group_size, audience, price, days_ago, duration) in enumerate(tours_data):
            Tour.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'date': now - timedelta(days=days_ago),
                    'group_size': group_size,
                    'conductor': emp2,
                    'season': season,
                    'audience': audience,
                    'price': price,
                    'duration_minutes': duration,
                },
            )
        for season_code, _ in SEASON_CHOICES:
            Tour.objects.filter(code=f'EX-{season_code.upper()}-001').delete()

        all_exhibits = list(Exhibit.objects.all().order_by('name'))
        permanent = [
            (
                'Зал древнего искусства',
                h1,
                date(2010, 1, 1),
                'Постоянная экспозиция античности и средневековья: керамика, металл, предметы культа. '
                'Зал поддерживает стабильный микроклимат и освещение для хрупких материалов.',
            ),
            (
                'Зал живописи',
                h2,
                date(2012, 6, 1),
                'Коллекция живописи XVIII–XX веков: портреты, пейзажи, акварели. '
                'Экспозиция выстроена хронологически и сопровождается кураторскими текстами.',
            ),
            (
                'Зал скульптуры',
                h3,
                date(2015, 3, 15),
                'Скульптура и декоративное искусство: бронза, мрамор, малые формы. '
                'Предусмотрены обзорные точки для рассмотрения объёмных работ.',
            ),
        ]
        for ex_name, hall, start, desc in permanent:
            exh, _ = Exhibition.objects.update_or_create(
                name=ex_name,
                defaults={'description': desc, 'hall': hall, 'start_date': start},
            )
            exh.description = desc
            exh.save(update_fields=['description'])

        ancient_names = {'Ваза керамическая', 'Подсвечник бронзовый', 'Ковёр ручной работы', 'Гравюра «Вид города»'}
        painting_names = {
            'Картина «Утро в лесу»', 'Портрет неизвестного', 'Пейзаж «Осень»', 'Акварель «Море»',
        }
        sculpture_names = {'Скульптура «Мыслитель»', 'Бюст поэта', 'Статуя «Ника»', 'Эскиз к фреске'}
        by_name = {ex.name: ex for ex in all_exhibits}

        def _link_exhibits(exhibition_name, names):
            exh = Exhibition.objects.filter(name=exhibition_name).first()
            if not exh:
                return
            for nm in names:
                ex = by_name.get(nm)
                if ex:
                    exh.exhibits.add(ex)

        _link_exhibits('Зал древнего искусства', ancient_names)
        _link_exhibits('Зал живописи', painting_names)
        _link_exhibits('Зал скульптуры', sculpture_names)

        Show.objects.update_or_create(
            name='Белорусские художники XX века',
            defaults={
                'description': 'Временная выставка живописи и графики белорусских мастеров второй половины XX века.',
                'start_date': date(2026, 7, 1),
                'end_date': date(2026, 10, 31),
            },
        )
        Show.objects.update_or_create(
            name='Сокровища запасников',
            defaults={
                'description': 'Редкие экспонаты из фондохранилища, представленные ограниченный срок.',
                'start_date': date(2026, 5, 15),
                'end_date': date(2026, 8, 15),
            },
        )
        for show in Show.objects.all():
            for ex in all_exhibits[:3]:
                show.exhibits.add(ex)

        Article.objects.get_or_create(
            title='Добро пожаловать в музей',
            defaults={
                'content': (
                    'Краткая информация о последней статье. '
                    'Музей приглашает посетителей на новую экспозицию современного искусства '
                    'и цикл субботних экскурсий для семей.'
                ),
                'is_published': True,
            },
        )
        CompanyInfo.objects.get_or_create(
            title='О нас',
            defaults={
                'content': (
                    'Музей искусств — культурное учреждение, собирающее и сохраняющее '
                    'произведения живописи, скульптуры и декоративно-прикладного искусства. '
                    'Мы проводим экскурсии, лекции и образовательные программы.'
                ),
                'order': 0,
            },
        )
        CompanyInfo.objects.get_or_create(
            title='Миссия',
            defaults={
                'content': 'Делать искусство доступным каждому посетителю через живой диалог с экспонатами.',
                'order': 1,
            },
        )

        profile, _ = CompanyProfile.objects.get_or_create(
            name='Музей искусств',
            defaults={
                'video_url': 'https://www.youtube.com/embed/ScMzIvxBSi4',
                'requisites': (
                    'УНП 100000000\n'
                    'р/с BY00 BANK 0000 0000 0000 0000 0000\n'
                    'Банк: ОАО «Банк»\n'
                    'Юр. адрес: г. Минск, ул. Культуры, 1'
                ),
                'certificate_text': CERTIFICATE_TEXT,
            },
        )
        if not profile.certificate_text:
            profile.certificate_text = CERTIFICATE_TEXT
            profile.save(update_fields=['certificate_text'])

        logo_src = static / 'images' / 'logo.png'
        if logo_src.exists() and not profile.logo:
            with logo_src.open('rb') as f:
                profile.logo.save('logo.png', File(f), save=True)

        history_items = [
            (1998, 'Основание музея', 'Открытие первых залов живописи.'),
            (2005, 'Расширение фонда', 'Добавлен зал скульптуры.'),
            (2015, 'Цифровой каталог', 'Запуск онлайн-описаний экспонатов.'),
            (2024, 'Обновление сайта', 'Появление личного кабинета и корзины билетов.'),
        ]
        for i, (year, title, desc) in enumerate(history_items):
            CompanyHistory.objects.get_or_create(
                year=year,
                title=title,
                defaults={'description': desc, 'order': i},
            )

        partners_data = [
            ('Государственный Эрмитаж', 'https://www.hermitagemuseum.org/', 'partner_hermitage.png', 1),
            ('Третьяковская галерея', 'https://www.tretyakovgallery.ru/', 'partner_tretyakov.png', 2),
            ('Музей Лувра', 'https://www.louvre.fr/', 'partner_louvre.png', 3),
        ]
        for name, url, filename, order in partners_data:
            partner, created = Partner.objects.get_or_create(
                name=name,
                defaults={'website_url': url, 'order': order, 'is_active': True},
            )
            src = static / 'images' / 'partners' / filename
            if src.exists() and (created or not partner.logo):
                with src.open('rb') as f:
                    partner.logo.save(filename, File(f), save=True)

        news_data = [
            ('Ночная экскурсия по залам', 'В субботу музей открывает двери после заката для особой программы.', 'news_night_tour.png'),
            ('Реставрация «Утра в лесу»', 'Хранители завершили консервацию знаменитого пейзажа.', 'news_restoration.png'),
            ('Детская мастерская', 'Юные посетители создадут открытки по мотивам экспонатов.', 'news_workshop.png'),
            ('Новая временная выставка', 'Открывается зал современного искусства с работами белорусских авторов.', 'news_exhibition.png'),
            ('Лекция о символизме', 'Куратор расскажет о скрытых смыслах полотен конца XIX века.', 'news_lecture.png'),
            ('Фестиваль «Ночь музеев»', 'Особая программа с концертами и мастер-классами до полуночи.', 'news_festival.png'),
            ('Цифровой каталог фонда', 'Часть коллекции доступна для онлайн-просмотра на сайте музея.', 'news_catalog.png'),
        ]
        self._ensure_real_photos(media, force=False)
        for title, summary, image_name in news_data:
            news, created = News.objects.get_or_create(
                title=title,
                defaults={
                    'summary': summary,
                    'content': self._news_content(title),
                },
            )
            news.summary = summary
            news.content = self._news_content(title)
            news.save(update_fields=['summary', 'content'])
            img_path = media / 'news' / image_name
            if img_path.exists():
                with img_path.open('rb') as f:
                    news.image.save(image_name, File(f), save=True)

        faq_data = [
            ('Что такое экспозиция?', 'Экспозиция — упорядоченный показ экспонатов в пространстве зала.'),
            ('Что такое аудиогид?', 'Аудиогид — портативное устройство или приложение с рассказом о залах.'),
            ('Как купить билет онлайн?', 'Выберите услугу в каталоге, добавьте в корзину и перейдите к оплате.'),
        ]
        for q, a in faq_data:
            FAQ.objects.get_or_create(question=q, defaults={'answer': a})

        contact_specs = [
            (
                'Иванов Иван Иванович',
                'Администратор музея — Главный администратор',
                '+375 (17) 327-42-18',
                'admin@museum.by',
                'Общие вопросы, бронирование экскурсий и организационные запросы.',
                0,
                'contacts/male_admin.png',
            ),
            (
                'Петрова Мария Сергеевна',
                'Экскурсовод',
                '+375 (33) 111-22-33',
                'petrova@museum.by',
                'Проводит обзорные и тематические экскурсии для детских и взрослых групп.',
                1,
                'contacts/female_guide.png',
            ),
            (
                'Смирнова Анна Владимировна',
                'Секретарь — Специалист приёмной',
                '+375 (17) 200-12-34',
                'reception@museum.by',
                'Запись на мероприятия, первичная консультация посетителей и партнёров.',
                2,
                'contacts/female_reception.png',
            ),
            (
                'Сидорова Елена Николаевна',
                'Хранитель зала древнего искусства',
                '+375 (29) 123-45-67',
                'sidorova@museum.by',
                'Консультации по фонду, учёт и сохранность экспонатов постоянной экспозиции.',
                3,
                'contacts/female_keeper.png',
            ),
            (
                'Ковалёв Пётр Петрович',
                'Начальник службы безопасности',
                '+375 (29) 900-11-22',
                'security@museum.by',
                'Охрана музейного комплекса, пропускной режим и безопасность посетителей.',
                4,
                'contacts/male_security.png',
            ),
            (
                'Новикова Ольга Игоревна',
                'Методист образовательных программ',
                '+375 (29) 555-66-77',
                'novikova@museum.by',
                'Разработка программ для школьников и семейных маршрутов.',
                5,
                'contacts/female_reception.png',
            ),
            (
                'Белов Артём Дмитриевич',
                'IT-специалист',
                '+375 (33) 444-55-66',
                'it@museum.by',
                'Поддержка сайта, электронных билетов и интерактивных стендов.',
                6,
                'contacts/male_admin.png',
            ),
            (
                'Морозова Татьяна Петровна',
                'Бухгалтер',
                '+375 (17) 333-44-55',
                'accounting@museum.by',
                'Финансовый учёт, отчётность и работа с контрагентами.',
                7,
                'contacts/female_keeper.png',
            ),
            (
                'Волков Сергей Александрович',
                'Реставратор',
                '+375 (29) 777-88-99',
                'volkov@museum.by',
                'Консервация и реставрация живописи и графики.',
                8,
                'contacts/male_security.png',
            ),
            (
                'Кузнецова Ирина Викторовна',
                'PR-менеджер',
                '+375 (44) 222-33-44',
                'pr@museum.by',
                'Связи с общественностью, пресс-релизы и социальные сети.',
                9,
                'contacts/female_guide.png',
            ),
            (
                'Лебедев Максим Олегович',
                'Кассир',
                '80291112233',
                'cashier@museum.by',
                'Продажа билетов, консультация по тарифам и промокодам.',
                10,
                'contacts/male_admin.png',
            ),
            (
                'Фёдорова Наталья Андреевна',
                'Куратор временных выставок',
                '+375 (29) 111 22 33',
                'fedorova@museum.by',
                'Организация выставок, работа с художниками и коллекционерами.',
                11,
                'contacts/female_reception.png',
            ),
        ]
        allowed_names = {spec[0] for spec in contact_specs}
        Contact.objects.exclude(name__in=allowed_names).delete()
        Contact.objects.filter(name='Администратор музея').delete()
        Contact.objects.filter(name='Сидоров Пётр Николаевич').delete()

        for name, role, phone, email, description, order, photo_rel in contact_specs:
            contact, _ = Contact.objects.update_or_create(
                name=name,
                defaults={
                    'role': role,
                    'phone': phone,
                    'email': email,
                    'description': description,
                    'order': order,
                },
            )
            contact.role = role
            contact.phone = phone
            contact.email = email
            contact.description = description
            contact.order = order
            contact.save()
            photo_path = photo_paths.get(photo_rel) or (media / photo_rel)
            if photo_path.exists():
                with photo_path.open('rb') as f:
                    contact.photo.save(Path(photo_rel).name, File(f), save=True)

        Vacancy.objects.update_or_create(
            title='Уборщик / Клинер музейных помещений',
            defaults={
                'description': (
                    'Обязанности: влажная и сухая уборка выставочных залов и служебных помещений; '
                    'соблюдение температурно-влажностного режима; аккуратное обращение с напольными '
                    'покрытиями и витринами.\n\n'
                    'Требования: аккуратность, ответственность, опыт работы приветствуется.'
                ),
                'is_active': True,
            },
        )
        Vacancy.objects.update_or_create(
            title='Экскурсовод',
            defaults={
                'description': (
                    'Обязанности: проведение обзорных и тематических экскурсий для детских и взрослых групп; '
                    'подготовка маршрутов и работа с аудиогидом.\n\n'
                    'Требования: высшее гуманитарное или историческое образование, грамотная речь, '
                    'опыт работы с аудиторией от 1 года.'
                ),
                'is_active': True,
            },
        )
        Vacancy.objects.get_or_create(
            title='Администратор кассы',
            defaults={
                'description': 'Продажа билетов, работа с промокодами, консультации посетителей.',
                'is_active': True,
            },
        )

        seen_contact_names = set()
        for duplicate in list(Contact.objects.all().order_by('order', 'pk')):
            key = duplicate.name.strip().lower()
            if key in seen_contact_names:
                duplicate.delete()
            else:
                seen_contact_names.add(key)

        PromoCode.objects.get_or_create(
            code='WELCOME10',
            defaults={'description': 'Скидка 10% для новых посетителей', 'discount_percent': Decimal('10'), 'is_active': True},
        )
        PromoCode.objects.get_or_create(
            code='MUSEUM5',
            defaults={'description': 'Фиксированная скидка 5 BYN', 'discount_amount': Decimal('5'), 'is_active': True},
        )
        PromoCode.objects.get_or_create(
            code='OLD5',
            defaults={'description': 'Архивный купон', 'discount_percent': Decimal('5'), 'is_active': False},
        )

        services = [
            ('Взрослый будни', Decimal('15.00'), 0, True, False, False, 'adult.png',
             'Входной билет для взрослых в будние дни. Доступ во все постоянные залы.'),
            ('Взрослый выходные', Decimal('20.00'), 5, True, False, False, 'weekend.png',
             'Входной билет в выходные и праздничные дни.'),
            ('Детский', Decimal('8.00'), None, False, True, False, 'child.png',
             'Билет для детей школьного возраста в сопровождении взрослого.'),
            ('Аудиогид', Decimal('5.00'), None, True, False, True, 'audio.png',
             'Аренда аудиогида на русском языке на время посещения.'),
            ('Студенческий', Decimal('10.00'), None, True, False, False, 'adult.png',
             'Льготный билет при предъявлении студенческого билета.'),
            ('Пенсионный', Decimal('10.00'), None, True, False, False, 'adult.png',
             'Льготный билет для пенсионеров.'),
            ('Семейный (2+2)', Decimal('45.00'), None, True, True, False, 'weekend.png',
             'Семейный абонемент: 2 взрослых и 2 детских билета.'),
            ('Ночная экскурсия', Decimal('25.00'), None, True, False, True, 'audio.png',
             'Тематическая экскурсия после закрытия музея.'),
            ('Фотосъёмка', Decimal('7.00'), None, False, False, True, 'audio.png',
             'Разрешение на фотосъёмку без вспышки в залах.'),
            ('VIP-обзор', Decimal('50.00'), None, True, False, True, 'weekend.png',
             'Индивидуальный обзор с куратором (до 5 человек).'),
            ('Групповой (10+)', Decimal('12.00'), None, True, False, False, 'adult.png',
             'Билет для организованных групп от 10 человек.'),
            ('Годовой абонемент', Decimal('120.00'), None, True, False, True, 'weekend.png',
             'Неограниченное посещение в течение 12 месяцев.'),
        ]
        for name, price, day, adult, child, extra, img_name, desc in services:
            obj, created = TicketPrice.objects.get_or_create(
                name=name,
                defaults={
                    'base_price': price,
                    'day_of_week': day,
                    'is_adult': adult,
                    'is_child': child,
                    'is_extra_service': extra,
                    'description': desc,
                },
            )
            if not obj.description:
                obj.description = desc
                obj.save(update_fields=['description'])
            img_src = media / 'services' / img_name
            if img_src.exists() and (created or not obj.image):
                with img_src.open('rb') as f:
                    obj.image.save(img_name, File(f), save=True)

        if not Review.objects.exists():
            Review.objects.create(
                author_name='guest',
                rating=5,
                text='Отличная экспозиция и удобная покупка билетов онлайн!',
            )

        self.stdout.write(self.style.SUCCESS(
            'Demo data loaded. Exhibits: %s, Services: %s, Partners: %s'
            % (Exhibit.objects.count(), TicketPrice.objects.count(), Partner.objects.count())
        ))
        logger.info('Demo data loaded. Exhibits: %s', Exhibit.objects.count())
