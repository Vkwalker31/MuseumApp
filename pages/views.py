"""
Представления общих страниц: главная, о компании, новости, словарь, контакты,
вакансии, отзывы (с формой добавления), промокоды, политика конфиденциальности.
Регистрация, личный кабинет.
"""
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from museum.models import TicketPrice
from .models import (
    Article,
    Partner,
    CompanyInfo,
    CompanyProfile,
    CompanyHistory,
    News,
    FAQ,
    Contact,
    Vacancy,
    Review,
    PromoCode,
)

logger = logging.getLogger('pages')


def home(request):
    """
    Главная: логотип, баннеры, каталог услуг, последняя статья, партнёры.
    """
    article = Article.objects.filter(is_published=True).order_by('-created_at').first()
    services = TicketPrice.objects.all().order_by('name')[:8]
    partners = Partner.objects.filter(is_active=True).order_by('order', 'name')
    profile = CompanyProfile.objects.first()
    banners = [
        {'src': 'images/banners/banner1.png', 'alt': 'Выставка месяца в музее', 'title': 'Выставка месяца'},
        {'src': 'images/banners/banner2.png', 'alt': 'Экскурсии для всех возрастов', 'title': 'Экскурсии'},
        {'src': 'images/banners/banner3.png', 'alt': 'Семейный билет со скидкой', 'title': 'Семейный билет'},
    ]
    return render(request, 'pages/home.html', {
        'article': article,
        'services': services,
        'partners': partners,
        'profile': profile,
        'banners': banners,
    })


def about(request):
    """О компании: блоки, профиль, история, видео, реквизиты, сертификат."""
    blocks = CompanyInfo.objects.all().order_by('order')
    profile = CompanyProfile.objects.first()
    history = CompanyHistory.objects.all().order_by('year', 'order')
    return render(request, 'pages/about.html', {
        'blocks': blocks,
        'profile': profile,
        'history': history,
    })


def news_list(request):
    """Новости: заголовок, краткое содержание, картинка."""
    qs = News.objects.all().order_by('-created_at')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(summary__icontains=search))
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'pages/news_list.html', {'page_obj': page_obj, 'search': search})


def news_detail(request, pk):
    """Полная статья новости (читать далее)."""
    news = get_object_or_404(News, pk=pk)
    return render(request, 'pages/news_detail.html', {'news': news})


def faq_list(request):
    """Словарь терминов / FAQ с датой добавления."""
    qs = FAQ.objects.all().order_by('-added_at')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(question__icontains=search) | Q(answer__icontains=search))
    return render(request, 'pages/faq_list.html', {'faq_list': qs, 'search': search})


def contacts(request):
    """Контакты: фото сотрудников, описание, телефоны, почта."""
    contacts_list = []
    seen_names = set()
    for contact in Contact.objects.all().order_by('order', 'pk'):
        key = contact.name.strip().lower()
        if key in seen_names:
            continue
        seen_names.add(key)
        contacts_list.append(contact)
    profile = CompanyProfile.objects.first()
    return render(request, 'pages/contacts.html', {
        'contacts_list': contacts_list,
        'profile': profile,
    })


def contacts_table(request):
    """Интерактивная таблица контактов (ЛР3)."""
    return render(request, 'pages/contacts_table.html')


@require_GET
def api_contacts(request):
    """JSON API для загрузки контактов в таблицу (ЛР3)."""
    seen_names = set()
    items = []
    for contact in Contact.objects.all().order_by('order', 'pk'):
        key = contact.name.strip().lower()
        if key in seen_names:
            continue
        seen_names.add(key)
        items.append({
            'id': contact.pk,
            'name': contact.name,
            'role': contact.role,
            'photo': contact.photo.url if contact.photo else '',
            'phone': contact.phone,
            'email': contact.email,
            'description': contact.description,
        })
    return JsonResponse({'contacts': items})


def js_lab(request):
    """Страница «Задания JS» — задания по изучению возможностей JS (ЛР3)."""
    return render(request, 'pages/js_lab.html')


def privacy(request):
    """Политика конфиденциальности музея."""
    return render(request, 'pages/privacy.html')


def vacancies(request):
    """Вакансии с описанием."""
    qs = Vacancy.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'pages/vacancies.html', {'vacancies': qs})


def reviews(request):
    """Список отзывов. Поиск и сортировка."""
    qs = Review.objects.all().order_by('-created_at')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(author_name__icontains=search) | Q(text__icontains=search))
    rating = request.GET.get('rating', '')
    if rating.isdigit() and 1 <= int(rating) <= 5:
        qs = qs.filter(rating=int(rating))
    sort = request.GET.get('sort', '-created_at')
    if sort in ('created_at', '-created_at', 'rating', '-rating'):
        qs = qs.order_by(sort)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'pages/reviews.html', {
        'page_obj': page_obj,
        'search': search,
        'rating': rating,
        'sort': sort,
    })


@login_required
def review_add(request):
    """Добавить отзыв (только для залогиненных). Валидация на сервере."""
    from .forms import ReviewForm
    form = ReviewForm(request.POST or None)
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.author_name = request.user.get_full_name() or request.user.username
        review.save()
        messages.success(request, 'Отзыв отправлен.')
        return redirect('pages:reviews')
    return render(request, 'pages/review_form.html', {'form': form})


def promo_list(request):
    """Промокоды и купоны: действующие и в архиве."""
    active = PromoCode.objects.filter(is_active=True).order_by('-created_at')
    archive = PromoCode.objects.filter(is_active=False).order_by('-created_at')
    return render(request, 'pages/promo_list.html', {'active': active, 'archive': archive})


def register(request):
    """Регистрация посетителя с профилем (18+, телефон)."""
    if request.user.is_authenticated:
        return redirect('pages:profile')
    from .forms import RegisterForm
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Регистрация завершена.')
        logger.info('User registered: %s', user.username)
        return redirect('pages:home')
    return render(request, 'pages/register.html', {'form': form})


@login_required
def profile(request):
    """Личный кабинет: для посетителя — покупки; для сотрудника — экспонаты."""
    from museum.utils import is_employee
    if is_employee(request.user):
        return redirect('museum:employee_my_exhibits')
    return redirect('museum:visitor_tickets')
