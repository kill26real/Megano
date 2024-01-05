from random import choices
from string import ascii_letters

from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, reverse
from rest_framework import status

from django.test import TestCase

class AuthTestCase(APITestCase):
    @classmethod
    def setUp(self) -> None:
        self.username = ''.join(choices(ascii_letters, k=10))
        self.password = ''.join(choices(ascii_letters, k=12))

    def test_login(self):
        User.objects.create_user(username=self.username, password=self.password)
        url = reverse("auth_app:login")
        data = {"username": self.username, "password": self.password}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RegisterTestCase(APITestCase):
    @classmethod
    def setUp(self) -> None:
        self.name = ''.join(choices(ascii_letters, k=8))
        self.username = ''.join(choices(ascii_letters, k=10))
        self.password = ''.join(choices(ascii_letters, k=12))

    def test_create_account(self):
        url = reverse("auth_app:register")
        data = {
            "name": self.name,
            "username": self.username,
            "password": self.password
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username=self.username).exists())








AuthTestCase().test_login()
RegisterTestCase().test_create_account()

