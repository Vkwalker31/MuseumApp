"""
URL-маршруты музея. Связь с представлениями через re_path (регулярные выражения).
"""
from django.urls import path, re_path
from . import views

app_name = 'museum'

urlpatterns = [
    path('', views.exhibit_list, name='exhibit_list'),
    re_path(r'^exhibit/(?P<pk>\d+)/$', views.exhibit_detail, name='exhibit_detail'),
    re_path(r'^exhibit/create/$', views.exhibit_create, name='exhibit_create'),
    re_path(r'^exhibit/(?P<pk>\d+)/edit/$', views.exhibit_edit, name='exhibit_edit'),
    re_path(r'^exhibit/(?P<pk>\d+)/delete/$', views.exhibit_delete, name='exhibit_delete'),
    re_path(r'^halls/?$', views.hall_list, name='hall_list'),
    re_path(r'^tours/?$', views.tour_list, name='tour_list'),
    re_path(r'^exhibitions/?$', views.exhibition_list, name='exhibition_list'),
    re_path(r'^admin/stats/?$', views.admin_stats, name='admin_stats'),
    re_path(r'^employee/exhibits/?$', views.employee_my_exhibits, name='employee_my_exhibits'),
    re_path(r'^employee/tours/?$', views.employee_my_tours, name='employee_my_tours'),
    re_path(r'^visitor/tickets/?$', views.visitor_tickets, name='visitor_tickets'),
    re_path(r'^ticket-prices/?$', views.ticket_prices, name='ticket_prices'),
    re_path(r'^statistics/?$', views.statistics_view, name='statistics'),
    re_path(r'^external-apis/?$', views.external_apis_view, name='external_apis'),
    re_path(r'^parallel-demo/?$', views.parallel_demo_view, name='parallel_demo'),
    re_path(r'^api/exhibits/?$', views.api_exhibits_json, name='api_exhibits'),
]
