"""
URL-маршруты общих страниц. Регулярные выражения для связи URL с представлениями.
"""
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'pages'

urlpatterns = [
    re_path(r'^$', views.home, name='home'),
    re_path(r'^about/?$', views.about, name='about'),
    re_path(r'^news/?$', views.news_list, name='news_list'),
    re_path(r'^news/(?P<pk>\d+)/?$', views.news_detail, name='news_detail'),
    re_path(r'^faq/?$', views.faq_list, name='faq_list'),
    re_path(r'^contacts/?$', views.contacts, name='contacts'),
    re_path(r'^contacts/table/?$', views.contacts_table, name='contacts_table'),
    re_path(r'^api/contacts/?$', views.api_contacts, name='api_contacts'),
    re_path(r'^js-lab/?$', views.js_lab, name='js_lab'),
    re_path(r'^privacy/?$', views.privacy, name='privacy'),
    re_path(r'^vacancies/?$', views.vacancies, name='vacancies'),
    re_path(r'^reviews/?$', views.reviews, name='reviews'),
    re_path(r'^reviews/add/?$', views.review_add, name='review_add'),
    re_path(r'^promo/?$', views.promo_list, name='promo_list'),
    re_path(r'^register/?$', views.register, name='register'),
    re_path(r'^profile/?$', views.profile, name='profile'),
]
