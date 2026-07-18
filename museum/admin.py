"""
Админ-панель музея: фильтры, встроенное редактирование связанных записей.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ArtType,
    Hall,
    EmployeePosition,
    Employee,
    Visitor,
    Exhibit,
    Exhibition,
    ExhibitionExhibit,
    Show,
    Tour,
    TicketPrice,
    TicketPurchase,
)


@admin.register(ArtType)
class ArtTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ['number', 'name', 'floor', 'area']
    list_filter = ['floor']
    search_fields = ['number', 'name']
    inlines = []  # ExhibitHallInline ниже


@admin.register(EmployeePosition)
class EmployeePositionAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class ExhibitInline(admin.TabularInline):
    model = Exhibit
    fk_name = 'guardian'
    extra = 0
    fields = ['name', 'art_type', 'hall', 'date_of_entry']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'position', 'hall', 'phone', 'email']
    list_filter = ['position', 'hall', 'hall__floor']
    search_fields = ['full_name', 'phone', 'email']
    raw_id_fields = ['user']
    inlines = [ExhibitInline]


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'birth_date', 'user', 'created_at']
    list_filter = ['birth_date']
    search_fields = ['full_name', 'phone', 'user__username']
    raw_id_fields = ['user']


class ExhibitHallInline(admin.TabularInline):
    model = Exhibit
    fk_name = 'hall'
    extra = 0
    fields = ['name', 'art_type', 'guardian', 'date_of_entry']


HallAdmin.inlines = [ExhibitHallInline]

@admin.register(Exhibit)
class ExhibitAdmin(admin.ModelAdmin):
    list_display = ['name', 'art_type', 'hall', 'guardian', 'date_of_entry', 'recently_added']
    list_filter = ['art_type', 'hall', 'date_of_entry']
    search_fields = ['name', 'description']
    list_editable = []  # recently_added только для отображения
    date_hierarchy = 'date_of_entry'
    raw_id_fields = ['guardian']

    def recently_added(self, obj):
        if not obj.date_of_entry:
            return '-'
        from datetime import timedelta
        from django.utils import timezone
        half_year_ago = timezone.localdate() - timedelta(days=180)
        return 'Да' if obj.date_of_entry >= half_year_ago else 'Нет'
    recently_added.short_description = 'Поступил за последние 6 мес.'


class ExhibitionExhibitInline(admin.TabularInline):
    model = ExhibitionExhibit
    extra = 1
    raw_id_fields = ['exhibit']


@admin.register(Exhibition)
class ExhibitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'hall', 'start_date', 'end_date']
    list_filter = ['hall']
    search_fields = ['name']
    inlines = [ExhibitionExhibitInline]


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date']
    list_filter = ['start_date']
    search_fields = ['name']
    filter_horizontal = ['exhibits']


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'date', 'group_size', 'conductor', 'season']
    list_filter = ['season', 'conductor']
    search_fields = ['code', 'name']
    date_hierarchy = 'date'
    raw_id_fields = ['conductor']


@admin.register(TicketPrice)
class TicketPriceAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_price', 'day_of_week', 'is_child', 'is_adult', 'is_extra_service']
    list_filter = ['is_child', 'is_adult', 'is_extra_service']


@admin.register(TicketPurchase)
class TicketPurchaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'tour', 'price', 'promo_code', 'purchased_at']
    list_filter = ['purchased_at']
    search_fields = ['user__username', 'promo_code']
    raw_id_fields = ['user', 'tour']
