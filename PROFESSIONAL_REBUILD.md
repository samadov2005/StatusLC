# 🔄 Professional Arxitektura Qayta Qurilishi

**StatusLC Learning Center - Yangi Professional Tizim**

---

## 📊 O'zgarishlar Xulosasi

### 1. **Status Enum'lari Kiritildi**

Har bir model uchun holat tizimi o'rnatildi:

#### Teacher Status
- `ACTIVE` (Faol) - Aktiv o'qituvchi
- `INACTIVE` (Nofaol) - Aktiv emas
- `LEAVE` (Ta'tilda) - Mehnat layohasida
- `TERMINATED` (Ishdan chiqarilgan) - Butunlay chiqarilgan

#### Student Status
- `ACTIVE` (Faol) - Aktiv darsga qatnashuvchi
- `INACTIVE` (Nofaol) - Hali faol emas
- `GRADUATED` (Bitirgan) - Kurs bitirgan
- `SUSPENDED` (To'xtatilgan) - Vaqtincha to'xtatilgan
- `DROPPED` (Tark etgan) - Kursni tark etgan

#### Payment Status
- `PAID` (To'langan) - Bayoni to'lanadi
- `PENDING` (Kutilmoqda) - Todirish kutilmoqda
- `OVERDUE` (Muddati o'tgan) - 30 kun o'tga o'tgan
- `PARTIAL` (Qisman) - Qisman to'langan

#### Attendance Status
- `PRESENT` (Hozir) - Darsga kelgan
- `ABSENT` (Yo'q) - Darsga kelmagan
- `LATE` (Kechiktirgan) - Kech kelgan
- `EXCUSED` (Bujanishli) - Oqlanuvchi-sabab

---

## 🗂️ Model Kengaytmalar

### **Teacher Model**

**Yangi Maydonlar:**
```python
email: EmailField (Unique) - Elektron pochta
address: TextField - Manzili
status: TeacherStatus - Holati
hourly_rate: DecimalField - Soat stavkasi
hire_date: DateField - Ishga olingan sana
created_by: ForeignKey - Kim yaratgan (Audit)
```

**Yangi Indekslar:**
- `(status)` - Holat bo'yicha qidirish
- `(email)` - Email bo'yicha topish

**Yangi Metodlar:**
- `get_active_groups_count()` - Faol guruhlar
- `get_total_students()` - Jami o'quvchi

---

### **Group Model**

**Yangi Maydonlar:**
```python
description: TextField - Tasnifi
day_of_week: CharField - Hafta kuni (Dushanba... Yakshanba)
start_time: TimeField - Boshlanish vaqti (18:00)
end_time: TimeField - Tugash vaqti (19:30)
max_students: IntegerField - Maksimal o'quvchi (1-100)
min_students: IntegerField - Minimal o'quvchi (5)
is_active: BooleanField - Faol yoki yo'q
start_date: DateField - Boshlangan sana
end_date: DateField - Tugagan sana (Optional)
tuition_fee: DecimalField - Oylik to'lov somiga
```

**O'chirildi:**
- `time` maydon → `start_time` va `end_time` ga almashtirildi

**Yangi Propertylar:**
- `student_count` - Hozirda faol o'quvchilar
- `available_seats` - Bo'sh o'rindiqlar
- `class_duration_hours` - Dars davomiyligi (soat)

---

### **Student Model**

**Yangi Maydonlar:**
```python
email: EmailField - Elektron pochta
date_of_birth: DateField - Tug'ilgan sana (Optional)
parent_name: CharField - Ota-onaning ismi
parent_email: EmailField - Ota-onaning elektron pochtasi
status: StudentStatus - Ro'yxatlanish holati
enrollment_date: DateField - Ro'yxatlanish sanasi
```

**Yangi Propertylar:**
- `full_name` - To'liq ismi
- `age` - Hisoblangan yosh

**Yangi Metodlar:**
- `get_unpaid_months(limit=3)` - To'lanmagan oylar
- `get_total_paid(year)` - Yillik jami to'lovlar

---

### **Payment Model**

**Yangi Maydonlar:**
```python
group: ForeignKey - Qaysi guruh uchun
status: PaymentStatus - To'lov holati (Paid/Pending/Overdue)
payment_method: CharField - To'lov usuli (Naqd/Karta/Transfer)
reference_number: CharField - Chek/Kvitansiya raqami
confirmed_at: DateTime - Tasdiqlangan sana
created_by: ForeignKey(User) - Kim qayd etgan (Audit)
```

**O'zgartirildi:**
- Unique Constraint: `(student, month)` → `(student, group, month)`
- `paid_at` har qachon avtomatik

**Yangi Metodlar:**
- `is_overdue` - 30 kun o'tdi mi?
- `mark_as_paid()` - To'lovni tasdiqlash

---

### **Attendance Model**

**O'chirildi:**
- `present` (Boolean) → `status` (AttendanceStatus Enum)

**Yangi Maydonlar:**
```python
status: AttendanceStatus - Present/Absent/Late/Excused
minutes_present: IntegerField - Darsda bo'l vaqti (minut)
recorded_by: ForeignKey(User) - Kim qayd etgan (Audit)
```

**Yangi Metodlar:**
- `get_attendance_percentage(start, end)` - Davomiylik foiz

---

## ✨ Yangi Modellar

### **Discount Model**

```python
name: CharField - Chegirma nomi
description: TextField - Tafsiloti
discount_type: CHOICES - Foiz yoki Soʻm
value: DecimalField - Chegirma miqdori
applicable_groups: M2M - Qaysi guruhga
applicable_students: M2M - Qaysi o'quvchiga
is_active: BooleanField
start_date, end_date: DateField - Amal davri

Metodlar:
- is_valid() - Bugun amal qiladi mi?
- calculate_discount_amount(amount) - Chegirma miqdori
```

**Misol:**
```
"Yangi o'quvchilar uchun 10% chegirma"
- 10% foiz chegirmasi
- English va Math guruhiga
- 2026-04-01 dan 2026-06-30 gacha
```

---

### **TeacherSalary Model**

```python
teacher: ForeignKey - O'qituvchi
month: DateField - Maoshi oyiga
teaching_hours: DecimalField - Dars soatlari
hourly_rate: DecimalField - Soat stavkasi
bonus: DecimalField - Bonus
deductions: DecimalField - Tahsil (Soliq...)
total_salary: DecimalField - Jami maoshi

Formulasi:
total_salary = (teaching_hours × hourly_rate) + bonus - deductions
```

**Misol:**
```
2026-04 uchun:
- 40 soat darslik
- 50,000 сўм/soat
- 200,000 сўм bonus
- 150,000 сўм soliq (deductions)

Jami = (40 × 50000) + 200000 - 150000 = 2,050,000 сўм
```

---

### **LearningCenter Model**

```python
name: CharField - Markazing nomi
description: TextField
email, phone: Contact
address: TextField
currency: CharField - Valyuta (UZS, USD...)
default_tuition_fee: DecimalField - O'nchalik to'lov

Vazifasi: Markazing umumiy ma'lumotlari (1ta yozuv)
```

---

## 🔧 Migration Qadamlari

### 1999. Migration Created: `0004_discount_learningcenter_teachersalary_and_more.py`

**A'jvobgan O'zgarishlar:**
- 3 yangi model yaratildi (Discount, LearningCenter, TeacherSalary)
- 35+ yangi maydon qo'shildi
- 7 yangi indeks yaratildi
- Unique constraints yangilandi

**Default Qiymatlar Belgilandi:**
- `Group.start_time` → `timezone.now().time()`
- `Group.end_time` → `timezone.now().time()`
- `Teacher.email` → `'noemail@example.com'` (update qiling!)
- `Teacher.hire_date` → `timezone.now().date()`

---

## ⚠️ Muhim: Email va Hire Date Yangilash

Eski o'qituvchilar uchun email va hire_date ni yangilang:

```sql
-- Admin ponaletida:
UPDATE core_teacher SET email = 'teacher1@yourschool.uz' WHERE id = 1;
```

Yoki Django shell:

```python
from core.models import Teacher

teachers = Teacher.objects.all()
for teacher in teachers:
    teacher.email = f"{teacher.first_name.lower()}@school.uz"
    teacher.hire_date = timezone.now().date()
    teacher.save()
```

---

## 🚀 Tizimni Ishga Tusurish

```bash
# 1. Yangilangan Python paketlarini o'rnatish
pip install -r requirements.txt

# 2. Migratsiyalarni qo'llash
python manage.py migrate --no-input

# 3. Admin foydalanuvchisini yaratish
python manage.py createsuperuser

# 4. Server ishga tusurish
python manage.py runserver

# 5. Admin paneliga kirish
http://localhost:8000/admin
# (username va password bilan)
```

---

## 📝 Benzeri Yangilashlar

### Teachers Admin Paneli

**Taramasi:**
```
Personal Information:
  - First Name, Last Name
  - Email, Phone
  - Address

Employment:
  - Status (Active/Inactive/Leave/Terminated)
  - Hire Date
  - Hourly Rate

Statistics:
  - Active Groups Count
  - Total Students
```

**Filtrlar:**
- By Status
- By Hire Date
- By Create Date

---

### Groups Admin Paneli

**Taramasi:**
```
Group Information:
  - Name, Description
  - Level

Schedule:
  - Day of Week
  - Start Time - End Time
  - Class Duration (auto-calculated)

Capacity:
  - Max Students
  - Min Students
  - Current Count
  - Available Seats

Teacher & Tuition:
  - Teacher Assignment
  - Monthly Fee

Status:
  - Is Active
  - Start Date
  - End Date
```

---

### Payments Admin Paneli

**Yangi Maydonlar:**
```
- Status Dropdown (Paid/Pending/Overdue/Partial)
- Payment Method (Cash/Card/Transfer/Mobile)
- Reference Number (Chek raqami)
- Confirmed At (Tasdiqlash vaqti)
- Group Assignment (Qaysi guruh)
- Created By (Kim qayd etgan)
```

**Status Rang Kodlashtirish:**
- 🟢 Paid (Yashil)
- 🟠 Pending (Apelsin)
- 🔴 Overdue (Qizil)
- 🔵 Partial (Mavi)

---

### Attendance Admin Paneli

**Yangi Maydonlar:**
```
- Status Dropdown (Present/Absent/Late/Excused)
- Minutes Present (Dars davomiyligi)
- Recorded By (Kim qayd etgan)
```

**Status Rang Kodlashtirish:**
- 🟢 Present (Yashil) - Hozir
- 🔴 Absent (Qizil) - Yo'q
- 🟠 Late (Apelsin) - Kech
- 🔵 Excused (Mavi) - Oqlanuvchi

---

## 💡 Miksizasi

### To'lov Quyidagi Shaklida Qaydialishi:

```python
from core.models import Payment, PaymentStatus
from datetime import date

# Naqd to'lovni qayd etish
payment = Payment.objects.create(
    student=student,                    # Qaysi o'quvchi
    group=student.group,                # Qaysi guruh
    amount=500000,                      # 500,000 сўм
    month=date(2026, 4, 1),            # 2026-aprel oyiga
    status=PaymentStatus.PENDING,      # Kutilmoqda
    payment_method='cash',             # Naqd
    reference_number='CHK-20260419-001', # Chek raqami
    notes='Darsxonada qabul qilindi'
)

# Keyinchalik tasdiqlash
payment.status = PaymentStatus.PAID
payment.confirmed_at = timezone.now()
payment.save()
```

---

## 🔒 Xavfsizlik E'tiborlar

✅ **Audit Trail** - Kim va qachon o'zgartirganligini saqlaydi:
- `created_by` field
- `created_at`, `updated_at` timestamps

✅ **To'lov Tarixini saqlash** - Barcha to'lovlar to'langan
- Bekor qilish mumkin emas
- Faqat qayd qilish mumkin

✅ **Davomiylik Tarixini Saqlash** - Dars registratsiyasi shartnomaga asosan

✅ **Role-based Permissions** - Foydalanuvchi roliga asosan:
- Admin - Barchasini ko'rish/tahrir  
- Teacher - O'z guruhlari
- Student - Shaxsiy ma'lumot

---

## 📞 Qo'shimcha Resurslar

- **Batafsil Arxitektura:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **API Misollari:** [API_EXAMPLES.md](API_EXAMPLES.md)
- **Deployment Qo'llanma:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **Sinov Qo'llanma:** [TESTING.md](TESTING.md)

---

**Status:** ✅ **READY**  
**Version:** 1.0 Professional  
**Last Updated:** 2026-04-19

