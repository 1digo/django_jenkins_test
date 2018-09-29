from time import sleep

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.utils import override_settings
from django.urls.base import reverse


class TestMainViews(TestCase):
    def test_create_user(self):
        # создаем пользователя
        data = {
            'username': 'username',
            'email': 'email@email.ru',
            'password': 'password',
        }
        self.client.post(reverse("users"), data)
        self.assertEqual(1, User.objects.count())

        # проверяем, что он создался с корректными данными
        user = User.objects.get()
        self.assertEqual(user.username, 'username')
        self.assertEqual(user.email, 'email@email.ru')

        # проверяем, что можем залогиниться
        logged = self.client.login(username='username', password='password')
        self.assertTrue(logged)
        self.client.logout()

    def test_list_users(self):
        # создаем двух пользователей
        user1 = User.objects.create_user(
            username='username1',
            email='email1@email.ru',
            password='password',
        )

        user2 = User.objects.create_user(
            username='username2',
            email='email2@email.ru',
            password='password',
        )

        #  проверяем, что они возвращаются в корректном порядке и количестве
        r = self.client.get(reverse("users"))
        data = r.json()
        self.assertEqual(2, len(data['users']))
        self.assertEqual(data['users'][0]['id'], user1.id)
        self.assertEqual(data['users'][1]['id'], user2.id)

    @override_settings(TRACKER_CACHE_TIMEOUT=1)
    def test_tracker_works(self):
        # создаем пользователя
        user = User.objects.create_user(
            username='username',
            email='email@email.ru',
            password='password',
        )

        # логинимся под ним
        self.client.login(username='username', password='password')

        # дергаем трекер
        self.client.post(reverse("tracker"))

        # проверяем, что при запросе статуса пользователя в трекере,
        # пользователь значится как активный
        r = self.client.get(reverse("tracker"), {
            'id': user.pk
        })
        self.assertEqual(200, r.status_code)

        # еще раз дергаем трекер
        self.client.post(reverse("tracker"))

        # проверяем, что через 2 секунды пользователь уже не значится залогиненым
        sleep(2)
        r = self.client.get(reverse("tracker"), {
            'id': user.pk
        })
        self.assertEqual(404, r.status_code)
