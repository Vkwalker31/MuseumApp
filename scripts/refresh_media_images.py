"""Обновить картинки в БД из static/ и media/ после замены ассетов."""
import os
import sys
from pathlib import Path

import django

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MuseumApp.settings')
django.setup()

from django.core.files import File  # noqa: E402
from museum.models import Exhibit, TicketPrice  # noqa: E402
from pages.models import Contact, News, Partner, CompanyProfile  # noqa: E402

static = BASE / 'static'
media = BASE / 'media'


def attach(model, field, path):
    if not path.exists():
        return False
    with path.open('rb') as f:
        getattr(model, field).save(path.name, File(f), save=True)
    return True


partners = {
    'Государственный Эрмитаж': static / 'images/partners/partner_hermitage.png',
    'Третьяковская галерея': static / 'images/partners/partner_tretyakov.png',
    'Музей Лувра': static / 'images/partners/partner_louvre.png',
}
for name, path in partners.items():
    p = Partner.objects.filter(name=name).first()
    if p:
        attach(p, 'logo', path)

services = {
    'Взрослый будни': media / 'services/adult.png',
    'Взрослый выходные': media / 'services/weekend.png',
    'Детский': media / 'services/child.png',
    'Аудиогид': media / 'services/audio.png',
}
for name, path in services.items():
    s = TicketPrice.objects.filter(name=name).first()
    if s:
        attach(s, 'image', path)

contacts = {
    'Иванов Иван Иванович': media / 'contacts/male_admin.png',
    'Петрова Мария Сергеевна': media / 'contacts/female_guide.png',
    'Смирнова Анна Владимировна': media / 'contacts/female_reception.png',
    'Сидорова Елена Николаевна': media / 'contacts/female_keeper.png',
    'Ковалёв Пётр Петрович': media / 'contacts/male_security.png',
}
for name, path in contacts.items():
    c = Contact.objects.filter(name=name).first()
    if c:
        attach(c, 'photo', path)

news_map = {
    'Ночная экскурсия по залам': media / 'news/news_night_tour.png',
    'Реставрация «Утра в лесу»': media / 'news/news_restoration.png',
    'Детская мастерская': media / 'news/news_workshop.png',
    'Новая временная выставка': media / 'news/news_exhibition.png',
    'Лекция о символизме': media / 'news/news_lecture.png',
    'Фестиваль «Ночь музеев»': media / 'news/news_festival.png',
    'Цифровой каталог фонда': media / 'news/news_catalog.png',
}
for title, path in news_map.items():
    n = News.objects.filter(title=title).first()
    if n:
        attach(n, 'image', path)

for i in range(1, 13):
    path = media / 'exhibits' / f'exhibit_{i:02d}.png'
    if not path.exists():
        continue
    ex = Exhibit.objects.order_by('pk')[i - 1:i].first()
    if ex:
        attach(ex, 'image', path)

profile = CompanyProfile.objects.first()
if profile:
    attach(profile, 'logo', static / 'images/logo.png')

print('Media refreshed from new assets.')
