from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

from ..views import login


class LogInTests(TestCase):
    def setUp(self):
        url = reverse('accounts:login')
        self.response = self.client.get(url)

    def test_login_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_login_url_resolves_login_view(self):
        view = resolve('/login/')
        self.assertEquals(view.func, login)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, AuthenticationForm)

    def test_form_inputs(self):
        '''
                The view must contain five inputs: 2 csrf, username,
                password, captcha_text
        '''
        self.assertContains(self.response, '<input', 5)
        self.assertContains(self.response, 'type="text"', 2)
        self.assertContains(self.response, 'type="password"', 1)


class SuccessfulLogInTests(TestCase):
    def setUp(self):
        url = reverse('accounts:login')
        data = {
            'username': 'hanh',
            'password': 'abcdef123456'
        }
        User.objects.create_user(**data)
        self.response = self.client.post(url, data, follow=True)
        self.home_url = reverse('boards:home')

    def test_redirection(self):
        self.assertRedirects(self.response, self.home_url)

    def test_user_active(self):
        response = self.client.get(self.home_url)
        user = response.context.get('user')
        self.assertTrue(user.is_active)


class InvalidLogInTests(TestCase):
    def setUp(self):
        url = reverse('accounts:login')
        data = {
            'username': 'hanh',
            'password': '',
        }
        User.objects.create_user(**data)
        self.response = self.client.post(url, data, follow=True)
        self.home_url = reverse('boards:home')

    def test_login_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)


