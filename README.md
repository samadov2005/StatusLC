# 🏫 StatusLC - O'quv Markazi IT Boshqaruv Tizimi

**Professional Django Learning Center Management System** | v1.0 Professional Edition

A comprehensive Django backend for learning center management with professional architecture, REST API, role-based access control, payment tracking, attendance management, and financial reporting.

## ✨ Professional Features

- **👥 Role-Based User Management**: Student, Teacher, Administrator roles with audit trails
- **📚 Group Management**: Organize students by proficiency level, schedule, capacity with tuition fees
- **👨‍🎓 Student Enrollment**: Full student profiles with parent information, enrollment tracking, and status management
- **💰 Payment Tracking**: Monthly payment management with status tracking (PAID/PENDING/OVERDUE/PARTIAL)
- **📊 Attendance System**: Comprehensive attendance tracking with status types (PRESENT/ABSENT/LATE/EXCUSED)
- **👨‍🏫 Teacher Management**: Teacher profiles, employment status, hourly rates, and group assignments
- **💸 Salary Calculation**: Automated teacher salary calculation (hours × rate + bonus - deductions)
- **🎁 Discount Management**: Flexible discount system (percentage/fixed amount) for groups or students
- **📈 Financial Reporting**: Detailed income, payment, and salary reports
- **🔐 Professional Security**: Encrypted passwords, audit trails, role-based permissions
- **🔍 Advanced Filtering**: Filter by status, date ranges, groups, students, etc.
- **📱 REST API**: Full-featured API with authentication and permissions
- **🎨 Admin Interface**: Professional Jazzmin admin dashboard with color-coded status fields
- **🤖 Telegram Integration**: Webhook support for Telegram bot notifications
- **🌐 Multi-language**: Uzbek and English language support

## Project Structure

```
statuslc/              # Django project settings and configuration
├── settings.py       # Project settings with security configurations
├── urls.py          # URL routing
└── wsgi.py          # WSGI application

accounts/             # User authentication and authorization
├── models.py        # User profile model
├── views.py         # Login, signup, dashboard views
├── forms.py         # Registration forms with validation
├── signals.py       # Auto-create user profiles
└── urls.py          # Authentication routes

core/                 # Core business logic
├── models.py        # Student, Teacher, Group, Payment, Attendance models
├── views.py         # REST API viewsets
├── serializers.py   # API serializers
└── urls.py          # API routes

telegram_bot/         # Telegram bot integration
├── views.py         # Webhook handler
└── urls.py          # Webhook routes

templates/            # HTML templates
└── accounts/
    ├── home.html
    ├── login.html
    ├── student_dashboard.html
    ├── student_signup.html
    └── teacher_dashboard.html
```

## Setup & Installation

### Prerequisites
- Python 3.8+
- pip or pipenv

### 1. Create Virtual Environment

```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Linux/macOS
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
```
DEBUG=False
DJANGO_SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
TELEGRAM_BOT_TOKEN=your-telegram-token
```

**Required**: `DJANGO_SECRET_KEY` must be set in production. Generate a secure key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

Server will be available at: `http://localhost:8000/`

## API Documentation

### Authentication

All API endpoints (except public ones) require authentication. Use session authentication:

```bash
# Login
POST /api-auth/login/

# Logout
GET /api-auth/logout/
```

### API Endpoints

#### Teachers
```
GET    /api/teachers/          # List all teachers (admin only)
POST   /api/teachers/          # Create teacher (admin only)
GET    /api/teachers/{id}/     # Teacher details
PUT    /api/teachers/{id}/     # Update teacher
DELETE /api/teachers/{id}/     # Delete teacher
```

#### Groups
```
GET    /api/groups/            # List groups
POST   /api/groups/            # Create group (admin only)
GET    /api/groups/{id}/       # Group details
PUT    /api/groups/{id}/       # Update group
DELETE /api/groups/{id}/       # Delete group
```

#### Students
```
GET    /api/students/                    # List students
POST   /api/students/                    # Create student (admin only)
GET    /api/students/{id}/               # Student details
PUT    /api/students/{id}/               # Update student
DELETE /api/students/{id}/               # Delete student
GET    /api/students/unpaid/?month=YYYY-MM-DD  # List unpaid students
```

#### Payments
```
GET    /api/payments/          # List payments
POST   /api/payments/          # Record payment
GET    /api/payments/{id}/     # Payment details
PUT    /api/payments/{id}/     # Update payment
DELETE /api/payments/{id}/     # Delete payment
```

#### Attendance
```
GET    /api/attendances/                 # List attendance
POST   /api/attendances/                 # Create attendance record
GET    /api/attendances/{id}/            # Attendance details
PUT    /api/attendances/{id}/            # Update attendance
DELETE /api/attendances/{id}/            # Delete attendance
GET    /api/attendances/?group=1&date=2026-04-18  # Filter by group and date
```

### Example: Check Unpaid Students

```bash
curl -H "Cookie: sessionid=YOUR_SESSION_ID" \
  "http://localhost:8000/api/students/unpaid/?month=2026-04-01"
```

Response:
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "full_name": "John Doe",
      "group": 2,
      "phone": "998901234567",
      ...
    }
  ]
}
```

## Admin Interface

Access the admin panel at: `/admin/`

Features:
- Manage users and profiles
- Create and organize groups
- Track students and payments
- View and manage attendance records
- Search functionality for quick navigation

## Web Interface

### For Students
- `/` - Home page
- `/signup/` - Registration
- `/login/` - Login
- `/student/dashboard/` - View group, schedule, payments, attendance
- `/logout/` - Logout

### For Teachers
- `/teacher/dashboard/` - View assigned groups and students

## Telegram Bot Integration

### Setup

1. Create a Telegram bot with @BotFather
2. Set environment variable:
   ```
   TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN
   ```

3. Configure webhook:
   ```
   POST https://api.telegram.org/botYOUR_TOKEN/setWebhook
   {
     "url": "https://yourdomain.com/telegram/YOUR_TOKEN/"
   }
   ```

4. The webhook handler is ready at: `/telegram/<token>/`

### TODO: Implement

- Handle bot commands for payment checks
- Send notifications to students/teachers
- Query student status

## Security Best Practices

✅ Implemented:
- Strong password validation
- CSRF protection enabled
- Secure session handling
- Admin-only API endpoints for sensitive operations
- User permission-based data filtering
- Logging for audit trails
- HTTPS-ready security headers

⚠️ Production Checklist:
- [ ] Set `DJANGO_SECRET_KEY` to a secure random value
- [ ] Set `DEBUG=False` in production
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Use environment-specific settings
- [ ] Enable HTTPS/SSL certificates
- [ ] Set `SECURE_SSL_REDIRECT=True`
- [ ] Configure proper database (PostgreSQL recommended)
- [ ] Set up proper logging and monitoring
- [ ] Configure email for notifications
- [ ] Use a production WSGI server (Gunicorn, uWSGI)

## Development

### Running Tests

```bash
python manage.py test
```

### Database Migrations

Create migrations after model changes:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Code Quality

Follow PEP 8 standards and use:
```bash
pip install black flake8
black .
flake8 .
```

## Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn statuslc.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "statuslc.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Build and run:
```bash
docker build -t statuslc .
docker run -p 8000:8000 statuslc
```

## Contributing

1. Create a feature branch
2. Make changes with tests
3. Submit a pull request

## License

Proprietary - Learning Center Management System

## Support

For issues or questions, contact the development team.

## Changelog

### v1.1.0 - Professional Improvements
- Added comprehensive security settings
- Implemented API authentication and permissions
- Enhanced model validation and documentation
- Improved error handling in views
- Added database indexes for performance
- Created environment configuration structure
- Enhanced serializers with additional fields
- Added logging throughout application

### v1.0.0 - Initial Release
- Basic models and REST API
- User authentication
- Admin interface with Jazzmin theme

