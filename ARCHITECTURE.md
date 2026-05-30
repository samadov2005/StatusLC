# 🏫 StatusLC - O'quv Markazi IT Arxitekturasi

**Professional Django Learning Center Management System**

---

## 📋 Umumiy Ma'lumot

StatusLC - o'quv markazlari uchun to'lik boshqaruv tizimi bo'lib, quyidagilarni o'z ichiga oladi:

- 👥 **Foydalanuvchi Boshqaruvi** - O'qituvchi, O'quvchi, Administrator rollarini o'z ichiga oladi
- 📚 **Guruh Boshqaruvi** - Kurs, jadval, sigim va tarkibi
- 💰 **To'lov Boshqaruvi** - Oylik to'lovlar, chegirmalar, to'lov statuslari
- 📊 **Davomiylik Tizimi** - Darsga da'vat, dars vaqti registratsiyasi
- 👨‍🏫 **O'qituvchi Maoshi** - Soat miqdori, bonus, tahbis
- 📈 **Hisobot va Statistika** - Kvartal va yillik analitika

---

## 🏗️ Arxitektura Qatlami

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Web UI)                         │
│  Templates (Bootstrap 5) - Admin Dashboard - Student Dashboard
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│               Django REST Framework API Layer               │
│  ViewSets • Serializers • Permissions • Authentication     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Business Logic Layer                        │
│  Models • Services • Validators • Signals                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Data Access Layer                          │
│  Django ORM • Managers • Querysets • Database Indexes      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Database Layer (SQLite/PostgreSQL)              │
│  Tables • Relationships • Indexes • Constraints             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗃️ Asosiy Modellar va Aloqalar

### 1. **Foydalanuvchi Boshqaruvi (Accounts App)**

#### `User` (Django's AUTH_USER_MODEL)
```python
- username: CharField (Unique)
- email: EmailField
- password: Hashed
- first_name, last_name: CharField
- is_staff, is_superuser, is_active: BooleanField
- created_at, updated_at: DateTime
```

#### `Profile` (Extended User)
```python
- user: OneToOneField(User)
- role: CHOICES [student, teacher, admin]
- phone: CharField (validated)
- created_at, updated_at: DateTime

Vazifalar:
- Foydalanuvchi roli va ma'lumotini saqlash
- Telegramga xabar jo'natishda telefon raqamini ishlatish
```

---

### 2. **O'quv Markazi Tashkiloti (Core App)**

#### `LearningCenter`
```python
- name: CharField (O'quv markazi nomi)
- description: TextField
- email, phone: Contact info
- address: TextField
- currency: CharField (default: 'UZS')
- default_tuition_fee: DecimalField
- created_at, updated_at: DateTime

Vazifa: Markazing umumiy ma'lumotlari (yagona yozuv)
```

---

### 3. **O'qituvchi Boshqaruvi**

#### `Teacher`
```python
- first_name, last_name: CharField
- email: EmailField (Unique)
- phone: CharField
- address: TextField
- status: CHOICES [active, inactive, leave, terminated]
- hourly_rate: DecimalField (Soatlik stavka)
- hire_date: DateField
- user: OneToOneField(User) - faqat admin
- created_at, updated_at: DateTime
- created_by: ForeignKey(User) - Audit trail

Indekslar:
- (first_name, last_name)
- status
- email

Metodlari:
- get_active_groups_count() - Faol guruhlar soni
- get_total_students() - Jami o'quvchi soni
```

---

### 4. **Guruh Boshqaruvi**

#### `Group`
```python
- name: CharField (e.g., 'English A1 Group 1')
- description: TextField
- level: CharField (A1, A2, B1, B2...)
- day_of_week: CHOICES [monday...sunday]
- start_time: TimeField
- end_time: TimeField
- max_students: IntegerField (1-100, default: 20)
- min_students: IntegerField (default: 5)
- teacher: ForeignKey(Teacher)
- is_active: BooleanField
- start_date: DateField
- end_date: DateField (Optional)
- tuition_fee: DecimalField (Oylik so'm)
- created_at, updated_at: DateTime

Indekslar:
- teacher
- level
- is_active

Xususiyatlari:
- student_count: Faol o'quvchilar soni
- available_seats: Bo'sh o'rindiqlar
- class_duration_hours: Dars davomiyligi (soat)
```

---

### 5. **O'quvchi Boshqaruvi**

#### `Student`
```python
- first_name, last_name: CharField
- email: EmailField (Optional)
- phone: CharField
- date_of_birth: DateField (Optional)
- parent_name: CharField
- parent_phone: CharField
- parent_email: EmailField
- group: ForeignKey(Group)
- status: CHOICES [active, inactive, graduated, suspended, dropped]
- enrollment_date: DateField
- user: OneToOneField(User) - faqat student
- created_at, updated_at: DateTime

Indekslar:
- group
- user
- status
- phone

Xususiyatlari:
- full_name: Property
- age: Hisoblangan yosh

Metodlari:
- is_paid_for_month(month_date): Oyni to'laganmi?
- get_unpaid_months(limit=3): To'langan bo'lmagan oylar
- get_total_paid(year=None): Yillik to'lovlar jami
```

---

### 6. **To'lov Boshqaruvi**

#### `Payment`
```python
- student: ForeignKey(Student)
- group: ForeignKey(Group)
- amount: DecimalField
- month: DateField (1-chi kun)
- status: CHOICES [paid, pending, overdue, partial]
- payment_method: CHOICES [cash, card, transfer, mobile, other]
- reference_number: CharField (Chek raqami)
- paid_at: DateTime (Auto-created)
- confirmed_at: DateTime (Optional)
- notes: TextField
- created_by: ForeignKey(User)
- created_at: DateTime

Unique Constraint:
- (student, group, month)

Indekslar:
- (student, month)
- month
- status

Xususiyatlari:
- is_overdue: 30 kun o'tganmi?

Metodlari:
- mark_as_paid(confirmed_at=None): To'lov tasdiqlash
```

**To'lov Statusi Zanjiri:**
```
PENDING → PARTIAL → PAID
    ↓
  OVERDUE
```

---

### 7. **Chegirma Boshqaruvi**

#### `Discount`
```python
- name: CharField
- description: TextField
- discount_type: CHOICES [percentage, fixed]
- value: DecimalField
- applicable_groups: ManyToManyField(Group)
- applicable_students: ManyToManyField(Student)
- start_date: DateField
- end_date: DateField (Optional)
- is_active: BooleanField
- created_at: DateTime

Metodlari:
- is_valid(): Bugun amal qiladimi?
- calculate_discount_amount(amount): Chegirma miqdori
```

---

### 8. **Davomiylik Tizimi**

#### `Attendance`
```python
- student: ForeignKey(Student)
- group: ForeignKey(Group)
- date: DateField
- status: CHOICES [present, absent, late, excused]
- note: CharField (Sababi)
- minutes_present: IntegerField (Darsda o'tgan vaqt)
- created_at, updated_at: DateTime
- recorded_by: ForeignKey(User) - Kim yozgan

Unique Constraint:
- (student, group, date)

Indekslar:
- (group, date)
- (student, date)
- status

Statik Metodlar:
- for_group_on_date(group, date): Shu kuni davomiylik

Metodlari:
- get_attendance_percentage(start_date, end_date): Davomiylik %
```

---

### 9. **O'qituvchi Maoshi Boshqaruvi**

#### `TeacherSalary`
```python
- teacher: ForeignKey(Teacher)
- month: DateField
- teaching_hours: DecimalField
- hourly_rate: DecimalField
- bonus: DecimalField
- deductions: DecimalField (Soliq va h.k.)
- total_salary: DecimalField (Hisoblangan)
- is_paid: BooleanField
- paid_at: DateTime (Optional)
- created_at: DateTime

Unique Constraint:
- (teacher, month)

Metodlari:
- calculate_total(): Jami maoshi hisoblash
  Formula: (teaching_hours * hourly_rate) + bonus - deductions
```

---

## 📊 Enum va Statuslar

### Status Enums

#### TeacherStatus
```python
ACTIVE = 'active'      # Faol
INACTIVE = 'inactive'  # Nofaol
LEAVE = 'leave'        # Ta'tilda
TERMINATED = 'terminated' # Ishdan chiqarilgan
```

#### StudentStatus
```python
ACTIVE = 'active'           # Faol
INACTIVE = 'inactive'       # Nofaol
GRADUATED = 'graduated'     # Bitirgan
SUSPENDED = 'suspended'     # To'xtatilgan
DROPPED = 'dropped'         # Tark etgan
```

#### PaymentStatus
```python
PAID = 'paid'         # To'langan
PENDING = 'pending'   # Kutilmoqda
OVERDUE = 'overdue'   # Muddati o'tgan
PARTIAL = 'partial'   # Qisman
```

#### AttendanceStatus
```python
PRESENT = 'present'   # Hozir
ABSENT = 'absent'     # Yo'q
LATE = 'late'         # Kechiktirgan
EXCUSED = 'excused'   # Bujanishli
```

---

## 🔐 Ruxsat va Autentifikatsiya

### Permission Patterns

```python
# Ro'yxat ko'rish
PublicReadOnly       - Barcha
IsAuthenticated      - Ro'yxatdan o'tkanlar
IsAdminUser          - Admin faqat
IsTeacherUser        - O'qituvchi faqat
IsStudentUser        - O'quvchi faqat

# Tahrirlash
IsOwner              - Shahsiy ma'lumot faqat
IsTeacherOrAdmin     - O'qituvchi yoki admin
IsAdmin              - Admin faqat
```

### Role-Based Access

```python
# Admin - Barchasini ko'radi va tahrirlaydi
# Teacher - O'z guruhlari va o'quvchilari
# Student - Shaxsiy ma'lumot va to'lovlar
```

---

## 📱 API Endpointlari

```
# O'qituvchi (Admin only)
GET/POST     /api/teachers/
GET/PUT      /api/teachers/{id}/

# Guruhlar
GET/POST     /api/groups/
GET/PUT      /api/groups/{id}/

# O'quvchilar
GET/POST     /api/students/
GET/PUT      /api/students/{id}/
GET          /api/students/unpaid/  - To'lanmagan

# To'lovlar
GET/POST     /api/payments/
GET/PUT      /api/payments/{id}/

# Davomiylik
GET/POST     /api/attendances/
GET/PUT      /api/attendances/{id}/
```

---

## 💾 Database Indekslar

```sql
Teacher:
  - (first_name, last_name)
  - (status)
  - (email)

Group:
  - (teacher)
  - (level)
  - (is_active)

Student:
  - (group)
  - (user)
  - (status)
  - (phone)

Payment:
  - (student, month)
  - (month)
  - (status)

Attendance:
  - (group, date)
  - (student, date)
  - (status)
```

---

## 🔄 Model Aloqalari Diagrammasi

```
User (Django's USER)
├── Profile (1:1)
│   └── role: [student, teacher, admin]
│
├── Teacher (1:1) [if teacher]
│   ├── Group (1:Many)
│   │   ├── Student (Many:Many)
│   │   │   ├── Payment (1:Many)
│   │   │   └── Attendance (1:Many)
│   │   └── Attendance (1:Many)
│   │
│   └── TeacherSalary (1:Many)
│
├── Student (1:1) [if student]
│   ├── Group (Many:1)
│   ├── Payment (1:Many)
│   └── Attendance (1:Many)
│
└── Admin (is_superuser)

LearningCenter (1 record)
├── Groups (1:Many)
│   └── Teachers (Many:1)
│   └── Students (Many:Many)
│
└── Discounts (1:Many)
    ├── Groups (Many:Many) [Optional]
    └── Students (Many:Many) [Optional]
```

---

## 📝 Audit Trail

Quyidagi modellar o'zgarish tarixini saqlaydi:

- **Teacher**: `created_by`, `created_at`, `updated_at`
- **Payment**: `created_by`, `paid_at`, `confirmed_at`
- **Attendance**: `recorded_by`, `created_at`, `updated_at`
- **TeacherSalary**: `created_at`

---

## 🔧 Texnologiyalar va Stack

```
Backend:
  - Django 4.2+ (ORM, Admin, Forms)
  - Django REST Framework (API)
  - django-jazzmin (Admin UI)
  - python-telegram-bot (Bot integration)
  - django-cors-headers (CORS)

Frontend:
  - Bootstrap 5 (CSS Framework)
  - HTML5/CSS/JavaScript
  - Uzbek Language Support

Database:
  - SQLite (Development)
  - PostgreSQL (Production)

Deployment:
  - Gunicorn (App Server)
  - Nginx (Reverse Proxy)
  - Git (Version Control)
```

---

## 🚀 Deployment Qadam-Qadam

### Mahalliy Ishida (Development)

```bash
# Setup
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your settings

# Initialize
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic

# Run
python manage.py runserver
# Visit: http://localhost:8000/admin
```

### Ishlab Chiqarish (Production)

```bash
# Install
pip install -r requirements.txt

# PostgreSQL
createdb statuslc_prod
# Update .env: DATABASE_URL=postgresql://...

# Migrate
python manage.py migrate

# Collect Static
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn statuslc.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4

# Nginx Configuration
# Point to Gunicorn on port 8000
```

---

## 📚 Foydalanish Misollari

### 1. O'quvchi Ro'yxatdan O'tish

```python
from django.contrib.auth.models import User
from accounts.models import Profile
from core.models import Student, Group

# User yaratish
user = User.objects.create_user(
    username='john_student',
    email='john@example.com',
    password='secure_pass'
)

# Profile yaratish (signals avtomatik qiladi)
profile = user.profile
profile.role = 'student'
profile.phone = '+998991234567'
profile.save()

# O'quvchi yaratish
group = Group.objects.get(name='English A1')
student = Student.objects.create(
    first_name='John',
    last_name='Doe',
    email='john@example.com',
    phone='+998991234567',
    parent_name='Jane Doe',
    parent_phone='+998991234568',
    group=group,
    user=user
)
```

### 2. To'lov Qayd Etish

```python
from core.models import Payment, PaymentStatus
from datetime import date

# To'lov yaratish
payment = Payment.objects.create(
    student=student,
    group=student.group,
    amount=500000,  # 500,000 сўм
    month=date(2026, 4, 1),
    status=PaymentStatus.PENDING,
    payment_method='cash',
    notes='Naqd to'lov (Cash payment)'
)

# To'lovi tasdiqlash
payment.mark_as_paid()
```

### 3. Davomiylik Yozish

```python
from core.models import Attendance, AttendanceStatus
from datetime import date

attendance = Attendance.objects.create(
    student=student,
    group=student.group,
    date=date.today(),
    status=AttendanceStatus.PRESENT,
    minutes_present=60,
    recorded_by=request.user
)
```

### 4. Unpaid Months

```python
# O'quvchining to'lanmagan oylarini bilish
unpaid = student.get_unpaid_months(limit_months=3)
for month in unpaid:
    print(f"To'lanmagan oy: {month.strftime('%Y-%m')}")
```

### 5. Davomiylik Statistika

```python
# 90 kun ichidagi davomiylik foizi
percentage = attendance_record.get_attendance_percentage()
print(f"Davomiylik: {percentage:.1f}%")
```

---

## 🔒 Security Features

✅ **Built-in Django Security**
- CSRF Protection
- SQL Injection Prevention  
- Password Hashing (PBKDF2)
- XSS Protection

✅ **Konfiguratsiya asosan**
- `SECRET_KEY` environment dan
- `DEBUG = False` production da
- `ALLOWED_HOSTS` o'rnatilgan
- HTTPS/HSTS enabled

✅ **Ruxsat Tizmi**
- Token-based Authentication (JWT optional)
- Role-based Access Control (RBAC)
- Permission Decorators
- Object-level Permissions

---

## 📞 Support & Changes

**Agar something doesn't work or changes needed:**

1. Katta o'zgarish - Migration kerak
2. Kichik o'zgarish - Models update
3. Bug fix - Git commit + test

Hamisha `.env` file ni update qiling!

---

**Version:** 1.0.0  
**Last Updated:** 2026-04-19  
**Language:** Uzbek + English  
**Status:** Production Ready ✅

