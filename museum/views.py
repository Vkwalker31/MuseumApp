"""
Представления музея: экспонаты, залы, экскурсии, статистика (для админа),
личные данные для сотрудника/посетителя. CRUD, поиск, сортировка.
"""
import logging
from datetime import timedelta
from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q, Sum, Avg
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods, require_GET

from .models import (
    Exhibit,
    Hall,
    Tour,
    Employee,
    ArtType,
    Exhibition,
    Show,
    TicketPurchase,
    TicketPrice,
    Visitor,
    SEASON_CHOICES,
)
from .utils import is_employee, is_admin

logger = logging.getLogger('museum')


def _mode(values):
    """Мода: наиболее частое значение."""
    if not values:
        return None
    from collections import Counter
    counts = Counter(values)
    return counts.most_common(1)[0][0]

def exhibit_list(request):
    """Список экспонатов. Для всех. Поиск и сортировка."""
    qs = Exhibit.objects.select_related('art_type', 'hall', 'guardian').order_by('name')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(art_type__name__icontains=search)
        )
    sort = request.GET.get('sort', 'name')
    if sort in ('name', '-name', 'date_of_entry', '-date_of_entry', 'art_type__name'):
        qs = qs.order_by(sort)
    paginator = Paginator(qs, 10)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    return render(request, 'museum/exhibit_list.html', {
        'page_obj': page_obj,
        'search': search,
        'sort': sort,
    })


def exhibit_detail(request, pk):
    """Детальная информация об экспонате."""
    exhibit = get_object_or_404(Exhibit.objects.select_related('art_type', 'hall', 'guardian'), pk=pk)
    return render(request, 'museum/exhibit_detail.html', {'exhibit': exhibit})


def hall_list(request):
    """Список залов. Для всех."""
    qs = Hall.objects.prefetch_related('exhibits').order_by('floor', 'number')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(
            Q(number__icontains=search)
            | Q(name__icontains=search)
        )
    floor = request.GET.get('floor', '')
    if floor.isdigit():
        qs = qs.filter(floor=int(floor))
    sort = request.GET.get('sort', 'floor')
    if sort in ('floor', '-floor', 'name', 'number', 'area'):
        qs = qs.order_by(sort)
    return render(request, 'museum/hall_list.html', {
        'halls': qs,
        'search': search,
        'floor': floor,
        'sort': sort,
    })


def tour_list(request):
    """Список проведённых экскурсий. Для всех."""
    qs = Tour.objects.select_related('conductor').order_by('-date')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(
            Q(code__icontains=search)
            | Q(name__icontains=search)
        )
    season = request.GET.get('season', '')
    if season in dict(SEASON_CHOICES):
        qs = qs.filter(season=season)
    sort = request.GET.get('sort', '-date')
    if sort in ('date', '-date', 'name', 'group_size'):
        qs = qs.order_by(sort)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'museum/tour_list.html', {
        'page_obj': page_obj,
        'search': search,
        'season': season,
        'sort': sort,
    })


def exhibition_list(request):
    """Список экспозиций и выставок."""
    exhibitions = Exhibition.objects.prefetch_related('exhibits').order_by('name')[:50]
    shows = Show.objects.prefetch_related('exhibits').order_by('-start_date')[:50]
    return render(request, 'museum/exhibition_list.html', {
        'exhibitions': exhibitions,
        'shows': shows,
    })


@user_passes_test(is_admin)
def admin_stats(request):
    """
    Статистика для админа: залы (кол-во экспонатов по залам после даты),
    экскурсии по сезонам, сотрудники по этажам и т.д.
    """
    from django.db.models import Count, Q

    # Экспонаты по залам, поступившие после заданной даты
    date_param = request.GET.get('date', '')
    exhibits_by_hall_after_date = []
    if date_param:
        try:
            from datetime import datetime
            after_date = datetime.strptime(date_param, '%Y-%m-%d').date()
            halls_with_count = Hall.objects.annotate(
                cnt=Count('exhibits', filter=Q(exhibits__date_of_entry__gte=after_date))
            ).filter(cnt__gt=0).order_by('floor', 'number')
            exhibits_by_hall_after_date = [(h, h.cnt) for h in halls_with_count]
        except ValueError:
            pass

    # Экскурсии по сезонам (общее количество за весь период)
    tours_total = Tour.objects.count()
    tours_by_season = list(
        Tour.objects.values('season').annotate(cnt=Count('id')).order_by('season')
    )

    # Сотрудники по этажам (параметр поиска floor)
    floor_param = request.GET.get('floor', '')
    employees_by_floor = []
    if floor_param.isdigit():
        employees_by_floor = Employee.objects.filter(hall__floor=int(floor_param)).select_related('hall', 'position')

    # Недавно поступившие экспонаты (последние 6 месяцев)
    half_year_ago = timezone.localdate() - timedelta(days=180)
    recent_exhibits = Exhibit.objects.filter(date_of_entry__gte=half_year_ago).select_related('art_type', 'hall', 'guardian')[:20]

    return render(request, 'museum/admin_stats.html', {
        'exhibits_by_hall_after_date': exhibits_by_hall_after_date,
        'date_param': date_param,
        'tours_total': tours_total,
        'tours_by_season': tours_by_season,
        'employees_by_floor': employees_by_floor,
        'floor_param': floor_param,
        'recent_exhibits': recent_exhibits,
    })


@login_required
def employee_my_exhibits(request):
    """Для сотрудника: экспонаты, за которыми закреплён текущий пользователь."""
    if not is_employee(request.user):
        return HttpResponseForbidden('Доступ только для сотрудников.')
    try:
        emp = request.user.employee_profile
    except Employee.DoesNotExist:
        return HttpResponseForbidden('Профиль сотрудника не найден.')
    exhibits = Exhibit.objects.filter(guardian=emp).select_related('art_type', 'hall').order_by('name')
    return render(request, 'museum/employee_my_exhibits.html', {'exhibits': exhibits})


@login_required
def employee_my_tours(request):
    """Для сотрудника: экскурсии, которые проводит текущий пользователь."""
    if not is_employee(request.user):
        return HttpResponseForbidden('Доступ только для сотрудников.')
    try:
        emp = request.user.employee_profile
    except Employee.DoesNotExist:
        return HttpResponseForbidden('Профиль сотрудника не найден.')
    tours = Tour.objects.filter(conductor=emp).order_by('-date')
    return render(request, 'museum/employee_my_tours.html', {'tours': tours})


@login_required
def visitor_tickets(request):
    """Для посетителя: покупки билетов и форма покупки."""
    if is_employee(request.user):
        return redirect('museum:employee_my_exhibits')
    purchases = TicketPurchase.objects.filter(user=request.user).select_related('tour').order_by('-purchased_at')
    from .forms import TicketBuyForm
    form = TicketBuyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        price = form.calculate_price()
        TicketPurchase.objects.create(
            user=request.user,
            tour=form.cleaned_data.get('tour'),
            price=price,
            promo_code=form.cleaned_data.get('promo_code') or '',
        )
        messages.success(request, f'Билет куплен на сумму {price}.')
        logger.info('Ticket purchased by %s for %s', request.user, price)
        return redirect('museum:visitor_tickets')
    return render(request, 'museum/visitor_tickets.html', {
        'purchases': purchases,
        'form': form,
    })


def ticket_prices(request):
    """Стоимость посещения: тарифы по дням недели, возрасту, доп. услугам."""
    prices = TicketPrice.objects.all().order_by('name')
    return render(request, 'museum/ticket_prices.html', {'prices': prices})


# --- CRUD для экспонатов (админ или через админку; для примера — только чтение для всех, создание/редактирование через админку) ---
# По заданию CRUD реализовать — можно ограничить создание/редактирование/удаление админом через админ-панель.
# Либо добавить формы на сайте для админа. Добавлю простой CRUD через представления для суперпользователя.

@user_passes_test(is_admin)
@require_http_methods(['GET', 'POST'])
def exhibit_create(request):
    """Создание экспоната (админ)."""
    from .forms import ExhibitForm
    form = ExhibitForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Экспонат создан.')
        return redirect('museum:exhibit_list')
    return render(request, 'museum/exhibit_form.html', {'form': form, 'title': 'Добавить экспонат'})


@user_passes_test(is_admin)
@require_http_methods(['GET', 'POST'])
def exhibit_edit(request, pk):
    """Редактирование экспоната (админ)."""
    from .forms import ExhibitForm
    obj = get_object_or_404(Exhibit, pk=pk)
    form = ExhibitForm(request.POST or None, request.FILES or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'Изменения сохранены.')
        return redirect('museum:exhibit_detail', pk=pk)
    return render(request, 'museum/exhibit_form.html', {'form': form, 'title': 'Редактировать экспонат', 'exhibit': obj})


@user_passes_test(is_admin)
@require_http_methods(['POST'])
def exhibit_delete(request, pk):
    """Удаление экспоната (админ)."""
    obj = get_object_or_404(Exhibit, pk=pk)
    obj.delete()
    messages.success(request, 'Экспонат удалён.')
    return redirect('museum:exhibit_list')


# --- Статистика для отображения (среднее, медиана, мода; популярные типы и т.д.) ---
def statistics_view(request):
    """Статистические показатели: экспонаты по типам искусства, экскурсии по сезонам, суммы продаж и т.д."""
    # Экспонаты в алфавитном порядке
    exhibits_alpha = list(Exhibit.objects.order_by('name').values_list('name', flat=True)[:100])
    # Посетители в алфавитном порядке + возраст
    visitors = Visitor.objects.order_by('full_name')
    visitor_ages = [v.age for v in visitors if v.age is not None]
    if visitor_ages:
        ages_sorted = sorted(visitor_ages)
        n = len(ages_sorted)
        avg_age = sum(visitor_ages) / n
        median_age = ages_sorted[n // 2] if n % 2 else (ages_sorted[n // 2 - 1] + ages_sorted[n // 2]) / 2
        mode_age = _mode(visitor_ages)
    else:
        avg_age = median_age = mode_age = None

    # Количество экспонатов по видам искусства
    exhibits_by_art_type = list(
        Exhibit.objects.values('art_type__name').annotate(cnt=Count('id')).order_by('-cnt')
    )
    most_popular_art = exhibits_by_art_type[0] if exhibits_by_art_type else None

    # Сумма продаж билетов
    ticket_stats = TicketPurchase.objects.aggregate(
        total_sum=Sum('price'),
        avg_price=Avg('price'),
        count=Count('id'),
    )
    prices_list = list(TicketPurchase.objects.values_list('price', flat=True))
    mode_price = _mode([float(p) for p in prices_list]) if prices_list else None
    if prices_list:
        prices_sorted = sorted(float(p) for p in prices_list)
        n = len(prices_sorted)
        median_price = prices_sorted[n // 2] if n % 2 else (prices_sorted[n // 2 - 1] + prices_sorted[n // 2]) / 2
    else:
        median_price = None

    # Размеры групп экскурсий: среднее, медиана, мода
    tour_sizes = list(Tour.objects.values_list('group_size', flat=True))
    if tour_sizes:
        tour_sizes_sorted = sorted(tour_sizes)
        n = len(tour_sizes_sorted)
        median_group = tour_sizes_sorted[n // 2] if n % 2 else (tour_sizes_sorted[n // 2 - 1] + tour_sizes_sorted[n // 2]) / 2
        avg_group = sum(tour_sizes) / len(tour_sizes)
        mode_group = _mode(tour_sizes)
    else:
        median_group = avg_group = mode_group = None

    # Прибыль по видам искусства (через экскурсии/билеты — упрощённо: популярность типа = cnt * условная ценность)
    # Для музея: какой тип экспонатов «приносит» больше — по числу связанных покупок нет прямой связи,
    # используем долю экспонатов как индикатор популярности и «вклада».
    most_profitable_art = most_popular_art

    chart_labels = [x['art_type__name'] or 'Без типа' for x in exhibits_by_art_type]
    chart_data = [x['cnt'] for x in exhibits_by_art_type]
    return render(request, 'museum/statistics.html', {
        'exhibits_alpha': exhibits_alpha,
        'visitors': visitors[:50],
        'avg_age': avg_age,
        'median_age': median_age,
        'mode_age': mode_age,
        'exhibits_by_art_type': exhibits_by_art_type,
        'most_popular_art': most_popular_art,
        'most_profitable_art': most_profitable_art,
        'ticket_stats': ticket_stats,
        'mode_price': mode_price,
        'median_price': median_price,
        'avg_group_size': avg_group if tour_sizes else None,
        'median_group_size': median_group if tour_sizes else None,
        'mode_group_size': mode_group if tour_sizes else None,
        'tour_count': len(tour_sizes),
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    })


def external_apis_view(request):
    """Страница с данными из 2 сторонних API (параллельный запрос через asyncio при наличии aiohttp)."""
    try:
        from .parallel_module import fetch_external_apis_parallel
        api1, api2 = fetch_external_apis_parallel()
    except ImportError:
        from .services import fetch_external_api_1, fetch_external_api_2
        api1 = fetch_external_api_1()
        api2 = fetch_external_api_2()
    return render(request, 'museum/external_apis.html', {
        'api1': api1,
        'api2': api2,
    })


def parallel_demo_view(request):
    """
    Доп. задание: страница без CSS для демонстрации параллельного кода (asyncio).
    """
    from .parallel_module import fetch_external_apis_parallel
    api1, api2 = fetch_external_apis_parallel()
    return render(request, 'museum/parallel_demo.html', {
        'api1': api1,
        'api2': api2,
    })


@require_GET
@login_required
def api_exhibits_json(request):
    """
    API проекта: список экспонатов в JSON.
    Ограничение: только для авторизованных пользователей (неавторизованным — 403).
    """
    exhibits = Exhibit.objects.select_related('art_type', 'hall').order_by('name')[:100]
    data = [
        {
            'id': e.id,
            'name': e.name,
            'art_type': e.art_type.name if e.art_type else None,
            'hall': str(e.hall) if e.hall else None,
            'date_of_entry': e.date_of_entry.isoformat() if e.date_of_entry else None,
        }
        for e in exhibits
    ]
    return JsonResponse({'exhibits': data})
