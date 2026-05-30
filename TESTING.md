# StatusLC Testing Guide

Comprehensive guide for testing the StatusLC application.

## Table of Contents
1. [Unit Testing](#unit-testing)
2. [API Testing](#api-testing)
3. [Integration Testing](#integration-testing)
4. [Manual Testing](#manual-testing)
5. [Performance Testing](#performance-testing)

## Unit Testing

### Setup

```bash
pip install pytest pytest-django pytest-cov
```

### Create Test Files

Tests should be organized as:
```
core/
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_serializers.py
│   └── test_utils.py

accounts/
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   └── test_forms.py
```

### Example: Model Testing

`core/tests/test_models.py`:
```python
import pytest
from django.utils import timezone
from core.models import Student, Group, Teacher, Payment


@pytest.mark.django_db
class TestStudentModel:
    """Test Student model methods and properties."""
    
    def setup_method(self):
        """Set up test data."""
        self.teacher = Teacher.objects.create(
            first_name="John",
            last_name="Doe"
        )
        self.group = Group.objects.create(
            name="English A1",
            time="18:00",
            level="Beginner",
            teacher=self.teacher
        )
        self.student = Student.objects.create(
            first_name="Jane",
            last_name="Smith",
            phone="998901234567",
            group=self.group
        )
    
    def test_student_creation(self):
        """Test student creation."""
        assert self.student.id is not None
        assert str(self.student) == "Jane Smith"
    
    def test_student_full_name(self):
        """Test full name property."""
        assert self.student.__str__() == "Jane Smith"
    
    def test_is_paid_for_month_true(self):
        """Test payment status when paid."""
        from datetime import date
        month_date = date(2026, 4, 1)
        
        Payment.objects.create(
            student=self.student,
            amount=50000,
            month=month_date
        )
        
        assert self.student.is_paid_for_month(month_date) is True
    
    def test_is_paid_for_month_false(self):
        """Test payment status when unpaid."""
        from datetime import date
        month_date = date(2026, 4, 1)
        
        assert self.student.is_paid_for_month(month_date) is False


@pytest.mark.django_db
class TestPaymentModel:
    """Test Payment model."""
    
    def setup_method(self):
        """Set up test data."""
        self.teacher = Teacher.objects.create(first_name="John", last_name="Doe")
        self.group = Group.objects.create(
            name="English A1",
            time="18:00",
            level="Beginner",
            teacher=self.teacher
        )
        self.student = Student.objects.create(
            first_name="Jane",
            last_name="Smith",
            phone="998901234567",
            group=self.group
        )
    
    def test_payment_creation(self):
        """Test payment record creation."""
        from datetime import date
        payment = Payment.objects.create(
            student=self.student,
            amount=50000,
            month=date(2026, 4, 1)
        )
        
        assert payment.id is not None
        assert payment.amount == 50000
    
    def test_payment_unique_constraint(self):
        """Test that only one payment per month per student is allowed."""
        from django.db import IntegrityError
        from datetime import date
        import pytest
        
        month = date(2026, 4, 1)
        Payment.objects.create(
            student=self.student,
            amount=50000,
            month=month
        )
        
        with pytest.raises(IntegrityError):
            Payment.objects.create(
                student=self.student,
                amount=60000,
                month=month
            )
```

### Example: View Testing

`core/tests/test_views.py`:
```python
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


@pytest.mark.django_db
class TestStudentViewSet:
    """Test Student API viewset."""
    
    def setup_method(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_list_students(self):
        """Test listing students."""
        response = self.client.get('/api/students/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_unpaid_students_invalid_month(self):
        """Test unpaid endpoint with invalid month."""
        response = self.client.get('/api/students/unpaid/?month=invalid')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest core/tests/test_models.py

# Run specific test class
pytest core/tests/test_models.py::TestStudentModel

# Run with coverage
pytest --cov=core --cov=accounts

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_payment"
```

## API Testing

### Using curl

```bash
# Get authentication token
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"yourpassword"}' \
  http://localhost:8000/api-auth/login/

# Test student endpoint
curl -H "Authorization: Token your-token" \
  http://localhost:8000/api/students/

# Test unpaid endpoint
curl -H "Authorization: Token your-token" \
  "http://localhost:8000/api/students/unpaid/?month=2026-04-01"
```

### Using Postman

1. Import the collection from workspace
2. Set authentication in Environment variables
3. Run requests with proper headers

### Using Python

```python
import requests
from datetime import date

# Session authentication
session = requests.Session()
login_data = {'username': 'admin', 'password': 'password'}
session.post('http://localhost:8000/api-auth/login/', data=login_data)

# Make API calls
response = session.get('http://localhost:8000/api/students/')
print(response.json())
```

## Integration Testing

Test complete workflows:

```python
@pytest.mark.django_db
def test_student_registration_and_payment():
    """Test complete workflow: signup -> payment -> attendance."""
    from django.contrib.auth.models import User
    from core.models import Student, Group, Teacher, Payment, Attendance
    from datetime import date
    
    # Create teacher and group
    teacher = Teacher.objects.create(first_name="John", last_name="Doe")
    group = Group.objects.create(
        name="English A1",
        time="18:00",
        level="Beginner",
        teacher=teacher
    )
    
    # Create user
    user = User.objects.create_user(
        username='jane_smith',
        email='jane@example.com',
        password='secure123'
    )
    user.first_name = 'Jane'
    user.last_name = 'Smith'
    user.save()
    
    # Create student profile
    student = Student.objects.create(
        user=user,
        first_name='Jane',
        last_name='Smith',
        phone='998901234567',
        group=group
    )
    
    # Set profile role
    user.profile.role = 'student'
    user.profile.phone = '998901234567'
    user.profile.save()
    
    # Record payment
    month = date(2026, 4, 1)
    payment = Payment.objects.create(
        student=student,
        amount=50000,
        month=month
    )
    
    # Mark attendance
    attendance = Attendance.objects.create(
        student=student,
        group=group,
        date=date(2026, 4, 18),
        present=True
    )
    
    # Verify
    assert student.is_paid_for_month(month) is True
    assert student.attendances.count() == 1
    assert user.profile.role == 'student'
```

## Manual Testing

### Test Checklist

#### User Authentication
- [ ] User can register as student
- [ ] User receives email confirmation (if enabled)
- [ ] User can login with credentials
- [ ] User can logout
- [ ] Session persists correctly
- [ ] Admin can create other users

#### Student Features
- [ ] Student can view dashboard
- [ ] Student sees up-to-date group information
- [ ] Student can view their payment history
- [ ] Student can see their attendance records

#### Teacher Features
- [ ] Teacher can view assigned groups
- [ ] Teacher can view students in their groups
- [ ] Teacher can record attendance
- [ ] Teacher can see payment status

#### Admin Features
- [ ] Admin can create/edit students
- [ ] Admin can create/edit groups
- [ ] Admin can manage teachers
- [ ] Admin can record payments
- [ ] Admin can mark attendance
- [ ] Admin can generate reports

#### API
- [ ] API endpoints accessible
- [ ] Authentication works
- [ ] Permissions enforced
- [ ] Filtering works
- [ ] Sorting works
- [ ] Pagination works

#### Telegram Bot (Optional)
- [ ] Bot responds to /start
- [ ] Bot responds to /help
- [ ] /unpaid command shows correct data
- [ ] Unknown commands return help message

### Test Data Script

```bash
# Generate test data
python manage.py shell

# In python shell:
from django.contrib.auth.models import User
from core.models import Teacher, Group, Student, Payment, Attendance
from datetime import date

# Create test user
user = User.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='testpass123'
)
user.first_name = 'Test'
user.last_name = 'User'
user.save()

# Create teacher
teacher = Teacher.objects.create(
    first_name='Ahmed',
    last_name='Hassan',
    phone='998901234567'
)

# Create group
group = Group.objects.create(
    name='English A1',
    time='18:00',
    level='Beginner',
    teacher=teacher
)

# Create student
student = Student.objects.create(
    user=user,
    first_name='Test',
    last_name='User',
    phone='998909999999',
    group=group
)

# Create payment
payment = Payment.objects.create(
    student=student,
    amount=50000,
    month=date(2026, 4, 1)
)

# Create attendance
attendance = Attendance.objects.create(
    student=student,
    group=group,
    date=date(2026, 4, 18),
    present=True
)

print("Test data created successfully!")
```

## Performance Testing

### Database Query Analysis

```python
from django.test.utils import override_settings
from django.test import TestCase
from django.db import connection
from django.test.utils import CaptureQueriesContext

@override_settings(DEBUG=True)
class QueryOptimizationTest(TestCase):
    def test_student_list_queries(self):
        """Check number of queries for listing students."""
        from core.models import Student
        
        with CaptureQueriesContext(connection) as context:
            list(Student.objects.all())
        
        # Should be minimal queries
        assert len(context) <= 2
```

### Load Testing

Using Apache Bench:

```bash
# Install
sudo apt install apache2-utils

# Test API endpoint
ab -n 1000 -c 10 -H "Authorization: Token your-token" \
  http://localhost:8000/api/students/
```

Using Locust:

```bash
pip install locust

# Create locustfile.py
```

```python
from locust import HttpUser, task, between

class StatusLCUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        self.client.post('/api-auth/login/', {
            'username': 'admin',
            'password': 'password'
        })
    
    @task
    def list_students(self):
        self.client.get('/api/students/')
    
    @task
    def list_groups(self):
        self.client.get('/api/groups/')
```

Run load test:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_DB: statuslc_test
          POSTGRES_USER: statuslc
          POSTGRES_PASSWORD: password
    
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-django pytest-cov
      
      - name: Run tests
        run: pytest --cov=core --cov=accounts
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Debugging

### Django Debug Toolbar

```bash
pip install django-debug-toolbar
```

Add to settings.py:
```python
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
```

### Logging

Check logs:
```bash
# Development
tail -f logs/django.log

# Production
sudo journalctl -u statuslc -f
```

## Troubleshooting

### Tests Not Running
```bash
# Check pytest configuration
pytest --version

# Run with verbose output
pytest -v

# Check for syntax errors
python -m py_compile tests/test_models.py
```

### Tests Slow
```bash
# Profile tests
pytest --durations=10

# Run faster
pytest -x  # Stop on first failure
pytest -n 4  # Use 4 processes (requires pytest-xdist)
```

### Database Issues
```bash
# Reset test database
pytest --reuse-db

# Clear cache
python manage.py clear_cache
```
