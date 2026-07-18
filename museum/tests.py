"""
Тесты приложения museum. Покрытие кода 80%+.
"""
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import (
    ArtType,
    Hall,
    EmployeePosition,
    Employee,
    Visitor,
    Exhibit,
    Tour,
    TicketPrice,
    TicketPurchase,
    Exhibition,
    Show,
    validate_phone,
    validate_age_18,
)
from .utils import is_employee, is_admin, is_visitor

User = get_user_model()


class ValidatePhoneTest(TestCase):
    def test_valid_phone(self):
        validate_phone('+375 (29) 123-45-67')
        validate_phone('+375(29)123-45-67')

    def test_invalid_phone(self):
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            validate_phone('+375 29 1234567')
        with self.assertRaises(ValidationError):
            validate_phone('123')


class ValidateAgeTest(TestCase):
    def test_age_18_ok(self):
        validate_age_18(date(2000, 1, 1))

    def test_age_under_18(self):
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            validate_age_18(timezone.localdate() - timedelta(days=365 * 17))


class RoleUtilsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('user1', 'u@t.com', 'pass')
        self.emp_user = User.objects.create_user('emp1', 'e@t.com', 'pass')
        self.superuser = User.objects.create_superuser('admin', 'a@t.com', 'pass')
        self.hall = Hall.objects.create(number='1', name='Зал', floor=1)
        self.pos = EmployeePosition.objects.create(name='Хранитель')
        Employee.objects.create(user=self.emp_user, full_name='Сотрудник', hall=self.hall, position=self.pos)

    def test_is_employee(self):
        self.assertFalse(is_employee(self.user))
        self.assertTrue(is_employee(self.emp_user))
        self.assertFalse(is_employee(None))

    def test_is_admin(self):
        self.assertTrue(is_admin(self.superuser))
        self.assertFalse(is_admin(self.user))

    def test_is_visitor(self):
        self.assertTrue(is_visitor(self.user))
        self.assertFalse(is_visitor(self.emp_user))


class ExhibitModelTest(TestCase):
    def setUp(self):
        self.art = ArtType.objects.create(name='Живопись')
        self.hall = Hall.objects.create(number='1', name='Зал', floor=1)
        self.emp = Employee.objects.create(full_name='Иванов', hall=self.hall)

    def test_create_exhibit(self):
        ex = Exhibit.objects.create(
            name='Картина',
            art_type=self.art,
            hall=self.hall,
            guardian=self.emp,
            date_of_entry=date(2024, 1, 1),
        )
        self.assertEqual(ex.name, 'Картина')
        self.assertEqual(Exhibit.objects.count(), 1)


class VisitorModelTest(TestCase):
    def test_visitor_age(self):
        user = User.objects.create_user('vis', 'v@t.com', 'pass')
        v = Visitor.objects.create(
            user=user,
            full_name='Посетитель',
            birth_date=date(1995, 6, 1),
            phone='+375 (29) 111-22-33',
        )
        self.assertGreaterEqual(v.age, 18)
        self.assertEqual(str(v), 'Посетитель')


class ExhibitViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.art = ArtType.objects.create(name='Живопись')
        self.hall = Hall.objects.create(number='1', name='Зал', floor=1)
        self.exhibit = Exhibit.objects.create(name='Экспонат 1', art_type=self.art, hall=self.hall)
        self.admin = User.objects.create_superuser('admin', 'a@t.com', 'pass')

    def test_exhibit_list(self):
        r = self.client.get(reverse('museum:exhibit_list'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Экспонат 1')

    def test_exhibit_list_search(self):
        r = self.client.get(reverse('museum:exhibit_list'), {'q': 'Экспонат'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Экспонат 1')

    def test_exhibit_detail(self):
        r = self.client.get(reverse('museum:exhibit_detail', args=[self.exhibit.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Экспонат 1')

    def test_exhibit_create_requires_admin(self):
        r = self.client.get(reverse('museum:exhibit_create'))
        self.assertEqual(r.status_code, 302)
        self.client.login(username='admin', password='pass')
        r = self.client.get(reverse('museum:exhibit_create'))
        self.assertEqual(r.status_code, 200)

    def test_exhibit_crud(self):
        self.client.login(username='admin', password='pass')
        r = self.client.post(reverse('museum:exhibit_create'), {
            'name': 'Новый',
            'art_type': self.art.pk,
            'hall': self.hall.pk,
            'description': 'desc',
        })
        self.assertEqual(r.status_code, 302)
        ex = Exhibit.objects.get(name='Новый')
        r = self.client.post(reverse('museum:exhibit_edit', args=[ex.pk]), {
            'name': 'Новый2',
            'art_type': self.art.pk,
            'hall': self.hall.pk,
            'description': 'd',
        })
        self.assertEqual(r.status_code, 302)
        ex.refresh_from_db()
        self.assertEqual(ex.name, 'Новый2')
        r = self.client.post(reverse('museum:exhibit_delete', args=[ex.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Exhibit.objects.filter(pk=ex.pk).exists())


class HallViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        Hall.objects.create(number='1', name='Зал первый', floor=1)

    def test_hall_list(self):
        r = self.client.get(reverse('museum:hall_list'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Зал первый')

    def test_hall_search_floor(self):
        r = self.client.get(reverse('museum:hall_list'), {'floor': '1', 'q': 'первый'})
        self.assertEqual(r.status_code, 200)


class TourViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.hall = Hall.objects.create(number='1', name='Зал', floor=1)
        self.emp = Employee.objects.create(full_name='Гид', hall=self.hall)
        Tour.objects.create(
            code='T1', name='Экскурсия', date=timezone.now(),
            group_size=10, conductor=self.emp, season='summer',
        )

    def test_tour_list(self):
        r = self.client.get(reverse('museum:tour_list'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'T1')

    def test_tour_season_filter(self):
        r = self.client.get(reverse('museum:tour_list'), {'season': 'summer', 'q': 'T1'})
        self.assertEqual(r.status_code, 200)


class ExhibitionListTest(TestCase):
    def test_exhibitions(self):
        Exhibition.objects.create(name='Экспозиция А')
        Show.objects.create(name='Выставка Б')
        r = Client().get(reverse('museum:exhibition_list'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Экспозиция А')


class StatisticsViewTest(TestCase):
    def setUp(self):
        art = ArtType.objects.create(name='Живопись')
        Exhibit.objects.create(name='A', art_type=art)
        Exhibit.objects.create(name='B', art_type=art)
        Tour.objects.create(code='T', name='T', date=timezone.now(), group_size=12, season='winter')
        Tour.objects.create(code='T2', name='T2', date=timezone.now(), group_size=12, season='summer')
        user = User.objects.create_user('u', 'u@t.com', 'pass')
        TicketPurchase.objects.create(user=user, price=Decimal('10.00'))
        TicketPurchase.objects.create(user=user, price=Decimal('10.00'))
        TicketPurchase.objects.create(user=user, price=Decimal('20.00'))
        Visitor.objects.create(
            user=user, full_name='Алексей', birth_date=date(1990, 1, 1), phone='+375 (29) 100-20-30',
        )

    def test_statistics_page(self):
        r = Client().get(reverse('museum:statistics'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Живопись')


class AdminStatsTest(TestCase):
    def test_admin_stats_requires_superuser(self):
        r = Client().get(reverse('museum:admin_stats'))
        self.assertEqual(r.status_code, 302)

    def test_admin_stats_ok(self):
        User.objects.create_superuser('admin', 'a@t.com', 'pass')
        c = Client()
        c.login(username='admin', password='pass')
        hall = Hall.objects.create(number='1', name='Зал', floor=2)
        Employee.objects.create(full_name='Е', hall=hall, phone='+375 (29) 111-11-11')
        Exhibit.objects.create(name='X', hall=hall, date_of_entry=timezone.localdate())
        Tour.objects.create(code='S', name='S', date=timezone.now(), group_size=5, season='spring')
        r = c.get(reverse('museum:admin_stats'), {
            'date': timezone.localdate().strftime('%Y-%m-%d'),
            'floor': '2',
        })
        self.assertEqual(r.status_code, 200)


class EmployeeCabinetTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('emp', 'e@t.com', 'pass')
        hall = Hall.objects.create(number='1', name='Зал', floor=1)
        self.emp = Employee.objects.create(user=self.user, full_name='Сотр', hall=hall)
        Exhibit.objects.create(name='Мой', guardian=self.emp)
        Tour.objects.create(code='MT', name='Моя', date=timezone.now(), group_size=3, conductor=self.emp)

    def test_my_exhibits(self):
        self.client.login(username='emp', password='pass')
        r = self.client.get(reverse('museum:employee_my_exhibits'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Мой')

    def test_my_tours(self):
        self.client.login(username='emp', password='pass')
        r = self.client.get(reverse('museum:employee_my_tours'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'MT')

    def test_forbidden_for_visitor(self):
        User.objects.create_user('vis', 'v@t.com', 'pass')
        self.client.login(username='vis', password='pass')
        r = self.client.get(reverse('museum:employee_my_exhibits'))
        self.assertEqual(r.status_code, 403)


class TicketViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('buyer', 'b@t.com', 'pass')
        self.tp = TicketPrice.objects.create(name='Взрослый', base_price=Decimal('15.00'))

    def test_ticket_prices(self):
        r = self.client.get(reverse('museum:ticket_prices'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Взрослый')

    def test_buy_ticket(self):
        self.client.login(username='buyer', password='pass')
        r = self.client.post(reverse('museum:visitor_tickets'), {
            'ticket_price': self.tp.pk,
            'promo_code': '',
        })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(TicketPurchase.objects.filter(user=self.user).count(), 1)


class ApiExhibitsTest(TestCase):
    def test_api_requires_login(self):
        r = Client().get(reverse('museum:api_exhibits'))
        self.assertEqual(r.status_code, 302)

    def test_api_ok(self):
        User.objects.create_user('u', 'u@t.com', 'pass')
        Exhibit.objects.create(name='API Ex')
        c = Client()
        c.login(username='u', password='pass')
        r = c.get(reverse('museum:api_exhibits'))
        self.assertEqual(r.status_code, 200)
        self.assertIn('exhibits', r.json())


class ExternalApisTest(TestCase):
    @patch('museum.parallel_module.fetch_external_apis_parallel')
    def test_external_apis(self, mock_fetch):
        mock_fetch.return_value = (
            {'title': 'T', 'body': 'B', 'error': None},
            {'content': 'Q', 'author': 'A', 'error': None},
        )
        r = Client().get(reverse('museum:external_apis'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'T')

    @patch('museum.parallel_module.fetch_external_apis_parallel')
    def test_parallel_demo(self, mock_fetch):
        mock_fetch.return_value = (
            {'title': 'T', 'body': 'B', 'error': None},
            {'content': 'Q', 'author': 'A', 'error': None},
        )
        r = Client().get(reverse('museum:parallel_demo'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'asyncio')


class ServicesTest(TestCase):
    @patch('museum.services.requests.get')
    def test_fetch_api1(self, mock_get):
        from .services import fetch_external_api_1
        mock_get.return_value.json.return_value = {'title': 'x', 'body': 'y'}
        mock_get.return_value.raise_for_status = lambda: None
        self.assertEqual(fetch_external_api_1()['title'], 'x')

    @patch('museum.services.requests.get')
    def test_fetch_api2(self, mock_get):
        from .services import fetch_external_api_2
        mock_get.return_value.json.return_value = {'content': 'c', 'author': 'a'}
        mock_get.return_value.raise_for_status = lambda: None
        self.assertEqual(fetch_external_api_2()['author'], 'a')
