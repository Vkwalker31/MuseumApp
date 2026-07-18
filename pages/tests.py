"""
Тесты приложения pages.
"""
from datetime import date

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Article, News, FAQ, Review, PromoCode, CompanyInfo, Contact, Vacancy
from museum.models import Visitor

User = get_user_model()


class HomeViewTest(TestCase):
    def test_home(self):
        r = Client().get(reverse('pages:home'))
        self.assertEqual(r.status_code, 200)

    def test_home_with_article(self):
        Article.objects.create(title='Тест', content='Текст', is_published=True)
        r = Client().get(reverse('pages:home'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Тест')


class AboutContactsVacanciesTest(TestCase):
    def test_about(self):
        CompanyInfo.objects.create(title='О нас', content='Текст', order=0)
        r = Client().get(reverse('pages:about'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'О нас')

    def test_contacts(self):
        Contact.objects.create(name='Иван', role='Гид', phone='+375 (29) 123-45-67')
        r = Client().get(reverse('pages:contacts'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Иван')

    def test_vacancies(self):
        Vacancy.objects.create(title='Гид', description='Работа', is_active=True)
        r = Client().get(reverse('pages:vacancies'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Гид')

    def test_privacy(self):
        r = Client().get(reverse('pages:privacy'))
        self.assertEqual(r.status_code, 200)


class NewsViewTest(TestCase):
    def test_news_list(self):
        r = Client().get(reverse('pages:news_list'))
        self.assertEqual(r.status_code, 200)

    def test_news_detail(self):
        n = News.objects.create(title='Новость', summary='Кратко', content='Полный текст')
        r = Client().get(reverse('pages:news_detail', args=[n.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Новость')

    def test_news_search(self):
        News.objects.create(title='Поиск', summary='Кратко', content='Текст')
        r = Client().get(reverse('pages:news_list'), {'q': 'Поиск'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Поиск')


class FAQViewTest(TestCase):
    def test_faq_list(self):
        FAQ.objects.create(question='Что?', answer='То')
        r = Client().get(reverse('pages:faq_list'), {'q': 'Что'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Что?')


class ReviewsViewTest(TestCase):
    def test_reviews_list(self):
        r = Client().get(reverse('pages:reviews'))
        self.assertEqual(r.status_code, 200)

    def test_review_add_requires_login(self):
        r = Client().get(reverse('pages:review_add'))
        self.assertEqual(r.status_code, 302)

    def test_review_add_post(self):
        user = User.objects.create_user('u', 'u@t.com', 'pass')
        c = Client()
        c.login(username='u', password='pass')
        r = c.post(reverse('pages:review_add'), {'rating': 5, 'text': 'Отличный музей!'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Review.objects.count(), 1)

    def test_reviews_filter(self):
        Review.objects.create(author_name='A', rating=5, text='ok')
        r = Client().get(reverse('pages:reviews'), {'rating': '5', 'q': 'ok'})
        self.assertEqual(r.status_code, 200)


class PromoViewTest(TestCase):
    def test_promo_list(self):
        PromoCode.objects.create(code='X', is_active=True)
        PromoCode.objects.create(code='Y', is_active=False)
        r = Client().get(reverse('pages:promo_list'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'X')


class RegisterViewTest(TestCase):
    def test_register_get(self):
        r = Client().get(reverse('pages:register'))
        self.assertEqual(r.status_code, 200)

    def test_register_post(self):
        r = Client().post(reverse('pages:register'), {
            'username': 'newuser',
            'full_name': 'Новый Пользователь',
            'birth_date': '1995-05-05',
            'phone': '+375 (29) 555-66-77',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertEqual(r.status_code, 302)
        user = User.objects.get(username='newuser')
        self.assertTrue(Visitor.objects.filter(user=user).exists())

    def test_register_underage(self):
        r = Client().post(reverse('pages:register'), {
            'username': 'kid',
            'full_name': 'Ребёнок',
            'birth_date': date.today().isoformat(),
            'phone': '+375 (29) 555-66-77',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.filter(username='kid').exists())


class ProfileViewTest(TestCase):
    def test_profile_redirect_visitor(self):
        User.objects.create_user('v', 'v@t.com', 'pass')
        c = Client()
        c.login(username='v', password='pass')
        r = c.get(reverse('pages:profile'))
        self.assertEqual(r.status_code, 302)
