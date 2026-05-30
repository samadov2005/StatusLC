import json

from django.contrib.auth import get_user_model
from django.test import TestCase


class OperatorAuthTests(TestCase):
    def make_user(self, username, password='Status123LC@2026', role=None, is_staff=False):
        user = get_user_model().objects.create_user(
            username=username,
            password=password,
            is_staff=is_staff,
        )
        user.profile.role = role
        user.profile.save()
        return user

    def test_operator_role_can_log_in_to_operator_cabinet(self):
        self.make_user('operator', role='operator')

        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'username': 'operator', 'password': 'Status123LC@2026'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['is_operator'])

    def test_non_operator_cannot_log_in_to_operator_cabinet(self):
        self.make_user('student', role='student')

        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'username': 'student', 'password': 'Status123LC@2026'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 403)

    def test_teacher_role_can_log_in_to_teacher_cabinet(self):
        self.make_user('teacher-login', role='teacher')

        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'username': 'teacher-login', 'password': 'Status123LC@2026'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['is_teacher'])
        self.assertEqual(response.json()['role'], 'teacher')
