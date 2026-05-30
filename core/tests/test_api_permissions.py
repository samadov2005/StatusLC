from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import Attendance, Group, Payment, Student, Teacher


class TeacherScopedApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.teacher_user = get_user_model().objects.create_user(
            username='teacher',
            password='Status123LC@2026',
        )
        self.teacher_user.profile.role = 'teacher'
        self.teacher_user.profile.save()

        other_user = get_user_model().objects.create_user(
            username='other-teacher',
            password='Status123LC@2026',
        )
        other_user.profile.role = 'teacher'
        other_user.profile.save()

        self.teacher = Teacher.objects.create(
            first_name='Ali',
            last_name='Valiyev',
            email='ali@example.com',
            phone='+998901112233',
            hire_date=timezone.localdate(),
            user=self.teacher_user,
        )
        other_teacher = Teacher.objects.create(
            first_name='Vali',
            last_name='Aliyev',
            email='vali@example.com',
            phone='+998901112244',
            hire_date=timezone.localdate(),
            user=other_user,
        )

        self.own_group = Group.objects.create(
            name='English A1',
            level='A1',
            day_of_week='monday',
            start_time='18:00',
            end_time='19:30',
            teacher=self.teacher,
        )
        other_group = Group.objects.create(
            name='English B1',
            level='B1',
            day_of_week='tuesday',
            start_time='18:00',
            end_time='19:30',
            teacher=other_teacher,
        )

        Student.objects.create(
            first_name='Own',
            last_name='Student',
            phone='+998901110001',
            group=self.own_group,
        )
        Student.objects.create(
            first_name='Other',
            last_name='Student',
            phone='+998901110002',
            group=other_group,
        )

    def test_teacher_sees_only_own_groups(self):
        self.client.force_authenticate(self.teacher_user)

        response = self.client.get('/api/groups/')

        self.assertEqual(response.status_code, 200)
        names = {item['name'] for item in response.json()['results']}
        self.assertEqual(names, {'English A1'})

    def test_teacher_sees_only_students_from_own_groups(self):
        self.client.force_authenticate(self.teacher_user)

        response = self.client.get('/api/students/')

        self.assertEqual(response.status_code, 200)
        names = {item['full_name'] for item in response.json()['results']}
        self.assertEqual(names, {'Own Student'})

    def test_teacher_cannot_create_group(self):
        self.client.force_authenticate(self.teacher_user)

        response = self.client.post('/api/groups/', {
            'name': 'IELTS Foundation',
            'level': 'B1',
            'day_of_week': 'friday',
            'start_time': '15:00',
            'end_time': '16:30',
            'teacher': self.teacher.id,
        }, format='json')

        self.assertEqual(response.status_code, 403)

    def test_teacher_can_record_attendance_for_own_group(self):
        self.client.force_authenticate(self.teacher_user)
        student = Student.objects.get(first_name='Own')

        response = self.client.post('/api/attendances/', {
            'student': student.id,
            'group': self.own_group.id,
            'date': timezone.localdate().isoformat(),
            'status': 'present',
            'homework_status': 'done',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        attendance = Attendance.objects.get(student=student, group=self.own_group)
        self.assertEqual(attendance.homework_status, 'done')


class OperatorApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.operator_user = get_user_model().objects.create_user(
            username='operator-api',
            password='Status123LC@2026',
        )
        self.operator_user.profile.role = 'operator'
        self.operator_user.profile.save()

        self.teacher = Teacher.objects.create(
            first_name='Dilshod',
            last_name='Karimov',
            email='dilshod@example.com',
            phone='+998901112255',
            hire_date=timezone.localdate(),
        )
        self.group = Group.objects.create(
            name='English Starter',
            level='A1',
            day_of_week='monday',
            start_time='09:00',
            end_time='10:30',
            teacher=self.teacher,
        )
        Student.objects.create(
            first_name='Aziza',
            last_name='Saidova',
            phone='+998901110010',
            group=self.group,
        )
        Student.objects.create(
            first_name='Javohir',
            last_name='Nazarov',
            phone='+998901110011',
            group=self.group,
        )

    def test_operator_can_create_group(self):
        self.client.force_authenticate(self.operator_user)

        response = self.client.post('/api/groups/', {
            'name': 'IELTS Intermediate',
            'level': 'B1',
            'day_of_week': 'wednesday',
            'start_time': '18:00',
            'end_time': '19:30',
            'teacher': self.teacher.id,
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Group.objects.filter(name='IELTS Intermediate').exists())

    def test_operator_can_create_group_with_multiple_schedule_days(self):
        self.client.force_authenticate(self.operator_user)

        response = self.client.post('/api/groups/', {
            'name': 'Kids English',
            'level': 'A1',
            'day_of_week': 'monday',
            'start_time': '15:00',
            'end_time': '16:30',
            'teacher': self.teacher.id,
            'schedules': [
                {'day_of_week': 'monday', 'start_time': '15:00', 'end_time': '16:30'},
                {'day_of_week': 'wednesday', 'start_time': '16:00', 'end_time': '17:30'},
            ],
        }, format='json')

        self.assertEqual(response.status_code, 201)
        group = Group.objects.get(name='Kids English')
        self.assertEqual(group.schedules.count(), 2)
        self.assertIn('Chorshanba', response.json()['schedule_display'])

    def test_operator_creates_teacher_with_login_password(self):
        self.client.force_authenticate(self.operator_user)

        response = self.client.post('/api/teachers/', {
            'first_name': 'Madina',
            'last_name': 'Sobirova',
            'email': 'madina@example.com',
            'phone': '+998901112266',
            'hire_date': timezone.localdate().isoformat(),
            'hourly_rate': '50000',
            'status': 'active',
            'username': 'madina.teacher',
            'password': 'Teacher123!',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        user = get_user_model().objects.get(username='madina.teacher')
        self.assertEqual(user.profile.role, 'teacher')
        self.assertTrue(user.check_password('Teacher123!'))

    def test_operator_can_assign_groups_when_updating_teacher(self):
        self.client.force_authenticate(self.operator_user)

        response = self.client.patch(f'/api/teachers/{self.teacher.id}/', {
            'assigned_groups': [self.group.id],
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.group.refresh_from_db()
        self.assertEqual(self.group.teacher_id, self.teacher.id)

    def test_public_overview_is_available_without_login(self):
        student = Student.objects.get(first_name='Aziza')
        Attendance.objects.create(
            student=student,
            group=self.group,
            date=timezone.localdate(),
            status='present',
            homework_status='done',
        )
        Payment.objects.create(
            student=student,
            group=self.group,
            amount='100000',
            month=timezone.localdate().replace(day=1),
            status='paid',
        )

        response = self.client.get('/api/public/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('groups', payload)
        student_payload = payload['groups'][0]['students'][0]
        self.assertIn('homework_status_display', student_payload)
        self.assertIn('payment_status', student_payload)

    def test_group_end_time_must_be_after_start_time(self):
        self.client.force_authenticate(self.operator_user)

        response = self.client.post('/api/groups/', {
            'name': 'Broken Schedule',
            'level': 'A2',
            'day_of_week': 'tuesday',
            'start_time': '18:00',
            'end_time': '17:30',
            'teacher': self.teacher.id,
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('end_time', response.json())

    def test_operator_can_search_students(self):
        self.client.force_authenticate(self.operator_user)

        response = self.client.get('/api/students/?search=Aziza')

        self.assertEqual(response.status_code, 200)
        names = {item['full_name'] for item in response.json()['results']}
        self.assertEqual(names, {'Aziza Saidova'})

    def test_operator_role_can_open_unpaid_report(self):
        self.client.force_authenticate(self.operator_user)

        response = self.client.get('/api/students/unpaid/?month=2026-05-01')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 2)
