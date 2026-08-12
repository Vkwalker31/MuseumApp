"""
Админ-панель общих страниц: новости, отзывы, промокоды и др.
"""
from django.contrib import admin
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


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'created_at', 'updated_at']
    list_filter = ['is_published']
    search_fields = ['title', 'content']


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'website_url', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name']


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    list_editable = ['order']


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(CompanyHistory)
class CompanyHistoryAdmin(admin.ModelAdmin):
    list_display = ['year', 'title', 'order']
    list_editable = ['order']
    ordering = ['year']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'summary', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'summary']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'added_at']
    search_fields = ['question', 'answer']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'phone', 'email', 'order']
    list_editable = ['order']


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['title']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['author_name', 'text']


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'description', 'is_active', 'discount_percent', 'valid_until']
    list_filter = ['is_active']
    search_fields = ['code']
